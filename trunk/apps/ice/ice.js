/*
	ice.js
*/

var jQ = jQuery;
var xForm = null;

jQ.attrSafe = function(s) { 
  s=s.replace(/&/g, "&amp;");
  s=s.replace(/'/g, "&apos;").replace(/\"/g, "&quot;");
  s=s.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return s;
}

var state = {hideClosedAnnotations:true};

jQ(iceMain);

// =======================================
// Main
// =======================================

function iceMain()
{
    var timingInfo = {toString:function(){ var r=""; for(var x in this) if(x!="toString") r+=x+" - "+this[x]+"\n"; return r; }};
    var iceMainStartTime = now();
    jQ("body:first").show();
    // get xForm
    xForm = getXForm();
    // setup/init actions
    var setupList = [timeTest, 
                    addBehaviours,              // FileManager
                    iceTabs,                    // Toolbar tabs
                    enableParaAnnotating,       // Annotations
                    tags,                       // Tags
                    showHide,                   // Show/Hide
                    gotoQueryStringLocation,    // Goto # location
                    workingStatusUpdate,        // Ajax processing update
                    oscar,
                    contentPositionUpdate,
                    timeTest ];
    timeFunction = function(func) {
        var startTime = now();
        var name = func.name;   // Note: firefox only (not IE)
        func();
        timingInfo[name] = now()-startTime;
    }
    jQ.map(setupList, timeFunction);
    timingInfo["iceMain(Total)"] = now()-iceMainStartTime;
    timingInfoResults = timingInfo;
}





// =======================================
// 
// =======================================



// =======================================
// Tests
// =======================================

function timeTest()
{
}



// =======================================
// 
// =======================================
function contentPositionUpdate(){
    if(jQ(".toolbar").css("position")=="fixed") {
        var x = jQ(".toolbar").height();
        jQ("body > div:first").css("height", x);
    }
}

function toolbarFloater()
{
    var toolbar = jQ(".toolbar");
    toolbar.css("position", "relative");
    toolbar.css("top", 0);
    var last = 0;
    jQ(window).scroll(function(){
        try {
            var x = window.scrollY;
            if (typeof(x)=="undefined") x = document.body.parentNode.scrollTop;
            //toolbar.css("top", x);
            //if(x<last) toolbar.css("top", 0);
            toolbar.animate({"top":x}, 10);
            last = x;
        } catch(e) {}
    });
}

// ======================================
// Alert messagebox 
// ======================================
function jQalert(message, title){

	var $=jQ;
    //set the messagebox div
    var divHTML = "<div id=\"popup_overlay\">";
    divHTML += "<div id=\"popup_title\" class='handle'>  </div><input type=\"button\" id=\"Esc_button\" value=\" x \" />";
    divHTML += "<div id=\"popup_content\">  </div>";
    divHTML += "<div id=\"popup_button\"><input id=\"ok_button\" type=\"button\" value=\"&nbsp;&nbsp;&nbsp;&nbsp;OK&nbsp;&nbsp;&nbsp;&nbsp;\" size=15px /></div>";
    divHTML += "</div>";
    $("body").append(divHTML);
    //set the message
    $("#popup_title").html(title);
    $("#popup_content").html(message);
    //show the box
    $("#popup_overlay").show();

    //message box related functions
    $("#ok_button").click( function() {
        $("#popup_overlay").hide();
        refresh();
    });
    $("#Esc_button").click( function() {
        $("#popup_overlay").hide();
        refresh();
    });

    //drag function
    $('#popup_overlay')
        .bind('dragstart',function( event ){
            return $(event.target).is('.handle');
        })
        .bind('drag',function( event ){
            $( this ).css({
            top: event.offsetY,
            left: event.offsetX
        });
    });

 }
 
// =======================================
// Atom Pub
// =======================================
 

// =======================================
// File Manager
// =======================================
// Note: some of the FileManager's functionality is in the toolbar (which is also handled here)
function addBehaviours()
{
  try 
  {
    xForm = getXForm();
    // toolbar sync
    jQ("button.ice-fm-sync").unbind().addClass("command").click(function() {  	
        var fileManagerView = jQ("div.app-file-manager").size()>0;
        if (!fileManagerView) { jQ("#ice_toolbar_status").addClass("update").text("Sync"); }
        
        function callback(data) {
            if (fileManagerView) {
                jQ("div.app-file-manager").replaceWith(data);
                workingStatusUpdate();
            } else {
                workingStatusUpdate(refresh);
            }   
        }
        xFormAjaxSubmit("sync", "", callback);
        
    });
    jQ("img.ice-fm-sync").unbind().addClass("command").click(function() {
        function callback(data) {
            jQ("div.app-file-manager").replaceWith(data);
            workingStatusUpdate();
        }
        xFormAjaxSubmit("syncSelected", "", callback)
    })
    var fm = jQ("div.app-file-manager");
    if(fm.size()==0)
    {
        //jQ("span.ice-fm-refresh").addClass("command").unbind().click( refresh );        // toolbar refresh
        return;
    }
    //jQ("span.ice-fm-refresh, img.ice-fm-refresh").addClass("command").unbind().click( function(){ xFormSubmit();} );

    // Added FileManager behaviours
    jQ("span.ice-fm-bAdd, button.ice-fm-bAdd").each(function() {
      var btn = jQ(this);
      btn.unbind();
      var btnId = btn.attr("id");
	  if (btnId=="cutSelected" || btnId=="copySelected") 
		{ btn.click(function() { xFormAjaxSubmit(this.id, "", cutCopyPasteCallback); }); }
      if (btnId=="updateSelected")
        {  
            if (jQ("div.app-file-manager").size()>0) { jQ("#ice_toolbar_status").remove(); }
            function callback(data) {
            	jQ("div.app-file-manager").replaceWith(data);
                workingStatusUpdate();
            }
            btn.click(function() { xFormAjaxSubmit(this.id, "", callback); }); 
        }
      if (btnId=="repairSelected"){
      	btn.click(function() {
      		var templateBox = jQ("select.ice-fm-dropBox").val();
      		xFormSubmit(this.id, "", templateBox); });
      }
	  else { btn.click(function() { xFormSubmit(this.id, ""); }); }
	});
	
    //
    var fmTable = fm.find("table.ice-file-manager");
    //fmTable.find("tr.file, tr.dir").click(function(e){ jQ(this).find(".select").click().change(); })
    //fmTable.find("td.ice-fm-cmd").click(function(e){ e.stopPropagation(); } )
    fmTable.find("tr.file, tr.dir").find("td:not(:eq(1), :eq(2), :eq(3))").click(function(e){ jQ(this).parent().find(".select").click().change(); })
    fmTable.find("td.ice-fm-cmd").find("span, img, label, select").each( function(i) {
	  var s = jQ(this);
	  var c = s.attr("class");
	  var id = null
	  function getTr() {
	    return s.parents("tr:first");
	  }
	  function getId(){
	    var tr = s.parents("tr:first");
	    id = tr.find("td input[@type='checkbox']").val();
        if(typeof(id)=="undefined")
        {
            id = tr.attr("id").substring(4);
        }
	    return id;
	  }
	  s.i = i
	  switch(c) {
	    case "paste":
	      s.click(function(){
		    var id = getId();
	 	    //unselectAll();
		    //xFormAjaxSubmit(c, id, cutCopyPasteCallback); 
		    xFormSubmit(c, id);
		  });
		  break;
	    case "copy":
	    case "cut":
	       s.click(function(){
		    var cb = s.parents("tr:first").find("td:first input[@type='checkbox']");
		    var id = getId();
	 	    unselectAll();
		    cb.attr("checked", true).change();
		    xFormAjaxSubmit(c, id, cutCopyPasteCallback); 
		   });
	       break;
  	    case "edit":
	      callback1=function(data, status){ 
            if(data.substring(0,12)=="redirectUrl="){  data=data.substring(12); window.location=data; }
          };
	      s.click(function(){
		    var id = getId();
		    xFormAjaxSubmit(c, id, callback1); 
		  });
	      break;
        case "download":
          s.click(function(){
            var id = getId();
            var xId = s.attr("id");
            var action = xForm.action;
            xForm.action += xId;
            xFormSubmit(c, id, xId);
            xForm.action = action;  // reset action
          });
          break;
	    case "delete":
	      s.click(function(){
		    var cb = s.parents("tr:first").find("td input[@type='checkbox']:first");
		    var id = getId();
            if (confirm("Are you sure you want to delete '" + id + "'?")) {
	 	      unselectAll();
		      cb.attr("checked", true).change();
		      xFormSubmit(c, id);
		    }
		  });
	      break;
	    case "options":
	      s.click(function(){
		      var tr = getTr();
		      jQ(this).parent().find("div.options").toggle().find(".log-data").hide();
              var renaming = tr.find(".renaming");
		      if(renaming.size()>0) { renaming.find("span.command").click(); }
	        });
	      break;
	    case "rename":
	      s.click(function(e){
		    var tr = getTr();
		    var d = tr.find("div.entry-name");
            var id = getId();
            if(d.hasClass("renaming"))
		    {
		      d.html(id);
		      d.removeClass("renaming");
		     // refresh();
		    }
		    else
		    {
		      d.addClass("renaming");
		      d.html("<div><input type='text' size='32' value='" + jQ.attrSafe(id) + "'/> <button>Save</button>&#160;<span class='command'>cancel</span></div>")
		      d.find("div").click(function(e){ return false;});
		      //d.find("span.command").click(renameClick);
		      
		      cancel = d.find("span.command");
		      cancel.click( function() {
		      	d.html(id);
		        d.removeClass("renaming");
		        
		        refresh();
		      });
		      
		      input = d.find("input");
		      input.focus()
		      save = d.find("button");
		      save.click( function(e) {
		      	var newName=d.find("input").val();
		      	newName = escape(newName);
		      	d.removeClass("renaming"); 
		      	d.find("div").hide();
			    d.append(newName);
			    //d.parent().parent().find(".options").click();
			    //xFormSubmit(c, id, newName);
			    function callback(data) {
			    	if (data.indexOf("Cannot rename")>-1){
			  	    	//alert(data); //If use confirm, it will have "ok and cancel" button.
			  	    		jQalert(data, "ICE Rename Error");
			  	    }else{
			  	    	refresh();
			  	    }
			  	}
			  	//alert(c + ", " + id + ", " + callback + ", " + newName);
			    xFormAjaxSubmit(c, id, callback, newName)
			  } );
			   
		      input.keypress(function(e){
		      	if(e.which == 13)
		      	{
		      		//save.click();  // not needed because inside a form
			    }
		      });
            }
		  });
	      break;
	    case "log":
	      var callback2=function(data, status){ s.parent().append(data); };
	      s.click(function(){
	       var me = jQ(this);
		   var logData = me.parent().find(".log-data")
		   if(logData.size()) logData.toggle();
		   else {var id = getId(); xFormAjaxSubmit(c, id, callback2);} 
	      });
	      break;
	    case "ice-content":
	        var callback2 = function(data, status){
                //var c=Boolean(parseInt(data)); s.find("input").attr("checked", c);
				refresh();
            }
	    	s.click(function(){
	    	   var id = getId();
			  	var state = Boolean(s.find("input").attr("checked"))
				xFormAjaxSubmit(c, id, callback2, state);
		      });
	    	break;
	    case "display-source-type":
	    case "links-as-endnotes":
        case "render-audio":
        case "glossary":
        case "glossary-terms":
	      var callback2 = function(data, status){
              var c=Boolean(parseInt(data)); s.find("input").attr("checked", c); }
	      // s.change doesn't work in IE..
	      s.click(function(e){ 
		  	    var id = getId();
			  	var state = Boolean(s.find("input").attr("checked"))
				//alert("change, "+c+", state="+state+", id="+id); 
				xFormAjaxSubmit(c, id, callback2, state); 
		  });
 	      break;
        case "tocLevels":
            s.change(function(e){
               var id = getId();
               var value = s.val();
               var callback = function(data, status){
                   s.val(data);
               }
               xFormAjaxSubmit(c, id, callback, value);
            });
            break;
        case "editBook":        // c=="editBook"
            s.click(function(){ var id=getId(); 
                gotoURI(id+"/"+c);
                //xForm.postCount.value = xForm.postCount.value*1+1;
                //xForm.action = id+"/"+c; 
                //xForm.submit();
            });
            break;
        case "revert":
            s.click(function(){ 
            	var id=getId(); 
            	if(confirm("Will revert to the repository version and local changes will be lost. Do you want to proceed?")){
            		xFormSubmit(c, id);
            	} 
            });
            break;
	    default:
            s.click(function(){ var id=getId(); xFormSubmit(c, id); });
	  }
      if(c=="disabled" || c=="revert disabled") {
      }
	  else {
        s.addClass("command");
      }
    });
    var pathPaste = jQ("div.app-nav img.paste");
    pathPaste.click(function() { xFormSubmit("paste", "."); });
	//binding the confirmation to click
	jQ("#revertSelected").mousedown(function(){
		if(confirm("Will revert to the repository version and local changes will be lost. Do you want to proceed?")){
			jQ("#revertSelected").click();
		}
	});
    iceFmSelect(fm);
  }
  catch(e)
  {
    alert("Error in addBehaviours() - " + e.message);
  }
  zebraTables();                // zebra strip tables
}


function iceFmSelect(fm)
{
    var selectAll = fm.find("input#selectAll");
    var selects = fm.find("input.select");
    var xSelectedBtns = jQ(".ice-fm-selected")
    var check = true;
    selectAll.unbind();
    selects.unbind();
    unselectAll = function() { selectAll.attr("checked", false); selectAll.change();}		// Global
    
    var checkSelected = function() // check if any selects elements are 'checked' or not
    {
	  if(selects.filter("*[@checked]").size()>0)
	  {
	    xSelectedBtns.removeClass("disabled"); 
	    xSelectedBtns.attr("disabled", false);
	  }
	  else
	  {
	    xSelectedBtns.addClass("disabled"); 
	    xSelectedBtns.attr("disabled", true);
	  }
	  //pasteEnable(false);
	  if (pasteNum>0) { xFormAjaxSubmit("deselect", "", cutCopyPasteCallback); }
    }

    selectAll.click(function(){
	var x;
	check = false;
        var chkList = xForm.selected;
        if(typeof(chkList.length)=="undefined") { chkList = [chkList]; }
	for(x=0; x<chkList.length; x++) {
	   var i=chkList[x];
	   if(i.checked!=this.checked) {  jQ(i).attr("checked", this.checked); jQ(i).change(); }
	}
	check = true;	
	checkSelected();
    });
 
    function changeState() {
        var x=jQ(this); tr=x.parents("tr:first");
        if(x.attr("checked"))	{
            if(tr.hasClass("alt"))
            {
                tr.addClass("alt-selected");
                tr.removeClass("alt");
            }
            else
            {
                tr.addClass("selected");
            }
        }else
        {
            if(tr.hasClass("alt-selected"))
            {
                tr.removeClass("alt-selected");
                tr.addClass("alt");
            }
            tr.removeClass("selected");
            selectAll.attr("checked", false);
        }	
        if (check) checkSelected();
     }
     selects.change(changeState);
     selects.click(changeState);    
     selects.click(function(e){e.stopPropagation();});
     pasteNum = 0;
     checkSelected();
     selects.change();
     pasteNum = jQ("#paste").attr("disabled") ? 0 : 1;
     pasteEnable(pasteNum);
}

function cutCopyPasteCallback(data, status)
{
  pasteNum =parseInt(data);
  pasteEnable(pasteNum);
}

function pasteEnable(enabled)
{
    if(enabled) {
      jQ(".ice-fm-paste").attr("disabled", false).removeClass("disabled"); 
      jQ("td.ice-fm-cmd span.paste, td.ice-fm-cmd img.paste, div.app-nav img.paste").show();
    }
    else {
      jQ(".ice-fm-paste").attr("disabled", true).addClass("disabled");
      jQ("td.ice-fm-cmd span.paste, td.ice-fm-cmd img.paste, div.app-nav img.paste").hide();
    }
}




// =======================================
// Toolbar (tabs etc)
// =======================================

var disabledToolbarInputs = null;
function disableToolbar()
{
  if(disabledToolbarInputs==null){
    disabledToolbarInputs = jQ("div.toolbar :input:enabled");
    disabledToolbarInputs.attr("disabled", true).addClass("disabled");
  }
}

function reEnableToolbar()
{
  if(disabledToolbarInputs==null) return;
    disabledToolbarInputs.attr("disabled", false).removeClass("disabled");
  disabledToolbarInputs = null;
}

function iceTabs()
{ 
  var toolbar = jQ("body > div.toolbar");
  var iceTabs = toolbar.find("div.ice-tabs:eq(0)")
  var tabCommonContent = iceTabs.find("div.ice-tab-common-content")
  var tabLinks = iceTabs.find("span.ice-tab");
  var tabContents = iceTabs.find("div.ice-tab-content");
  if(tabContents.size()==0)
  {
    tabContents = tabLinks.parent().next("div.ice-tab-content");
    if(tabContents.size()==0) return;
  }

  selectTab = function(tab, content) 
  { 
	tabContents.hide(); tab._content.show();
        setCookie("first", "first");
        setCookie("selectedTabId", tab.attr("id"));
	tabLinks.addClass("ice-tab-inactive"); tabLinks.removeClass("ice-tab-active");
	tab.removeClass("ice-tab-inactive"); tab.addClass("ice-tab-active");
  }
  // Add the onclick event handlers
  tabLinks.each(function(){ 
		var t=jQ(this); 
		t._content=toolbar.find("#" + t.attr("id") + "-content");
		t.click(function(){selectTab(t);}); 
	});

  var defaultTab = tabLinks.filter(".ice-tab-default:first");
  try
  {
    selectedTabId = readCookie("selectedTabId", defaultTab.attr("id"))
    selectedTab = toolbar.find("#" + selectedTabId)
    selectedTab._content = toolbar.find("#" + selectedTabId + "-content");
    selectTab(selectedTab);
  } catch (e)
  {
    defaultTab._content = defaultTab.next("div.ice-tab-content");
    selectTab(defaultTab);
  }
  toolbar.find("div.ice-tabs:eq(0)").append(tabContents);

// "ice-fm-fv"  // FileManager FileView
  if(!xForm) 
  {
    toolbar.find(".ice-fm-fv").click(function(){document.location=toolbar.find("#directory").val();});
  }
}


// =======================================
// Annotating
// =======================================

function enableParaAnnotating()
{
    //return;     // off for now
    // High para
    var annotations = {}
    var bodyDiv = jQ("div.body > div:first");
    var last = null;
    var annotateDiv = "<div class='annotate-form' style='background-color: transparent;'><textarea cols='80' rows='8'></textarea><br/>";
    annotateDiv += "<button class='cancel'>Cancel</button>&#160;"
    annotateDiv += "<button class='submit'>Submit</button> <span class='info'></span>"
    annotateDiv += "</div>";
    annotateDiv = jQ(annotateDiv);
    var textArea = annotateDiv.find("textarea");
    var unWrapLast = function() { if(last!=null){last.parent().replaceWith(last); last=null;} }
    var decorateAnnotation = function(anno) {
        var d;
        if (anno.hasClass("closed")) d = jQ("<span>&#160; <span class='delete-annotate command'> Delete</span></span>");
        else d = jQ("<span>&#160;<span class='close-annotate command'>Close</span>&#160;<span class='annotate-this command'>Reply</span></span>");
        anno.find("div.anno-info:first").append(d);
        var deleteClick = function(e) {
            var id = anno.attr("id");
            jQ.post(window.location+"?", {func:"inlineAnnotation", ajax:"1", id:id, action:"delete"},
                 function(rt){if(rt=="Deleted") {anno.remove(); } }, "text");
        }
        var closeClick = function(e) { 
            var id = anno.attr("id");
            var callback = function(responseText, statusCode) { 
                var updatedAnno = jQ(responseText);
                decorateAnnotation(updatedAnno);
                anno.replaceWith(updatedAnno);
                updatedAnno.find("div.inline-annotation").each(function(c){ var anno=jQ(this); decorateAnnotation(anno); });
            }
            jQ.post(window.location+"?", {func:"inlineAnnotation", ajax:"1", id:id, action:"close"},
                callback, "text");
        }
        var replyClick = function(e) {
            var id = anno.attr("id");
            annotate(anno);
        }
        d.find("span.close-annotate").click(closeClick);
        d.find("span.annotate-this").click(replyClick);
        d.find("span.delete-annotate").click(deleteClick);
    }
    var attachAnnotation = function(anno, para) {
        if(typeof(para)!="undefined" && para.size()>0) {
            if(para.hasClass("inline-annotation")) {
                para.find(">div.anno-children").prepend(anno);
            } else {
                if(!para.parent().hasClass("inline-anno")) {
                    para.wrap("<div class='inline-anno'/>");
                    //para.wrap("<div class='inline-anno'/>");
                }
                para.after(anno);
                para.css("margin", "0px");
            }
        }
    }
    var annotate = function(me) {
            if(last!=null) { annotateDiv.find("button.close").click(); unWrapLast(); }
            var id = me.attr("id");
            if(typeof(id)=="undefined") { return; }
            var closeClick = function() { annotations[id] = jQ.trim(textArea.val()); unWrapLast(); }
            var submitClick = function() { 
                unWrapLast(); 
                annotations[id] = "";
                var url = window.location;
                var text = jQ.trim(textArea.val());
                if(text=="") return;
                var html = me.wrap("<div/>").parent().html();    // Hack to access the outerHTML
                me.parent().replaceWith(me);
                var d = {func:"inlineAnnotation", ajax:"1", paraId:id, html:html, text:text, action:"add" };
                var callback = function(responseText, statusCode) { 
                    var anno = jQ(responseText);
                    decorateAnnotation(anno);
                    attachAnnotation(anno, me);
                }
                url = url + "?"
                jQ.post(url, d, callback, "text");
            }
            var restore = function() { 
                if(id in annotations) {textArea.val(annotations[id]);} else {textArea.val("");} 
            }
            restore();
            // wrap it
            me.wrap("<div class='inline-annotation-form'/>");
            me.parent().append(annotateDiv);
            annotateDiv.find("button.clear").click(function(){textArea.val("");});
            annotateDiv.find("button.cancel").click(function(){textArea.val(annotations[id]); closeClick();});
            annotateDiv.find("button.close").click(closeClick);
            annotateDiv.find("button.submit").click(submitClick);
            me.parent().prepend("<div class='app-label'>Comment on this:</div>");
            unWrapLast();
            last = me;
            textArea.focus();
    }
    var click = function(e) { 
        var t = e.target;
        var me = jQ(t).parent();
        var name = me[0].tagName;
        if (name=="P" || name=="DIV" || name.substring(0,1)=="H"){
            removePilcrow();
            // me
            annotate(me);
        } else {
            alert(name);
        }
        return false;
    }
    //bodyDiv.hover(hoverEnter, hoverLeave);
    var getSelectedText = function(){
        if(window.getSelection) return window.getSelection();
        if(document.getSelection) return document.getSelection();
        if(document.selection) return document.selection.createRange().text;
        return "";
    }
    var pilcrowSpan = jQ("<span class='pilcrow command'> &#xb6;</span>");
    var prTimer = 0;
    var addPilcrow = function(jqe) { if(prTimer)clearTimeout(prTimer); jqe.append(pilcrowSpan); 
                                        pilcrowSpan.unbind(); pilcrowSpan.click(click); 
                                        pilcrowSpan.mousedown(function(e){ return false; });
                                        pilcrowSpan.mouseup(click);     // for I.E.
                                   }
    var removePilcrow = function() { prTimer=setTimeout(function(){prTimer=0; pilcrowSpan.remove();}, 100); }
    bodyDiv.mouseover(function(e) { 
        var t = e.target;
        var name = t.tagName;
        if(name!="P" && name.substring(0,1)!="H") { if(t.parentNode.tagName=="P") t=t.parentNode; else return;}
        {
            var me = jQ(t);
            if(me.html()=="") return;
            me.unbind();
            me.mouseover(function(e) { if(getSelectedText()=="") addPilcrow(me); return false;} );
            me.mouseout(function(e) { removePilcrow(); } );
            me.mousedown(function(e) { removePilcrow(); } );
            me.mouseover();
        }
    });
    // enable annotations for the Title as well
    var titles = jQ("div.title");
    var title1 = titles.filter(":eq(0)");
    var title2 = titles.filter(":eq(1)");
    var titleId = title2.attr("id");
    if(typeof(titleId)=="undefined") titleId="h_titleIdt";
    titleId = titleId.toLowerCase();
    title2.attr("id", "_" + titleId);
    title1.attr("id", titleId);
    title1.mouseover(function(e) {
        var pilcrow = jQ("<span class='pilcrow command'> &#xb6;</span>");
        var me = jQ(e.target);
        me.unbind();
        
        me.mouseover(function(e) { if(getSelectedText()=="") addPilcrow(me); return false;} );
        me.mouseout(function(e) { removePilcrow(); } );
        me.mousedown(function(e) { removePilcrow(); } );
        me.mouseover();
    });
    //
    var commentOnThis = jQ("div.annotateThis");
    commentOnThis.find("span").addClass("command");
    commentOnThis.find("span").click(click);
    //
    // Show inline annotations
    //
    var inlineAnnotations = jQ("div.inline-annotations div.inline-annotation");
    inlineAnnotations.each(function(c){ var anno=jQ(this); decorateAnnotation(anno)});
    var inlineAnnotations = jQ("div.inline-annotations > div.inline-annotation");
    inlineAnnotations.each(function(c) {
        var me = jQ(this);
        var parentId = me.find("input[@name='parentId']").val();
        var p = bodyDiv.find("#" + parentId);
        if(parentId==titleId) p = title1;
        if(p.size()==0) {       // if orphan
            me.find("div.orig-content").show();
            bodyDiv.append(me);
        }
        attachAnnotation(me, p);
    });
    function hideShowAnnotations() {
        var me = jQ(this);
        var text = me.text();
        var inlineAnnotations = jQ("div.inline-annotation");
        var l = inlineAnnotations.size();
        var h = inlineAnnotations.filter(".closed").size();
        if(text.substring(0,1)=="H") {
            me.text("Show comments ("+(l-h)+" opened, "+h+" closed)");
            inlineAnnotations.hide();
        }
        else {
            me.text("Hide comments ("+(l-h)+" opened, "+h+" closed)");
            inlineAnnotations.show();
        }
    }
    jQ("div.ice-toolbar .hideShowAnnotations").click(hideShowAnnotations).text("S").click();
}

var visibleInlineAnnotations=null;
function hideVisibleAnnotations() {
    if(visibleInlineAnnotations!=null) return;
    visibleInlineAnnotations = jQ("div.inline-annotation:visible");
    visibleInlineAnnotations.hide();
}
function showVisibleAnnotations() {
    if(visibleInlineAnnotations==null) return;
    visibleInlineAnnotations.show();
    visibleInlineAnnotations = null;
}

// =======================================
// Ajax
// =======================================

function workingStatusUpdate(finishedCallback)      // Ajax working status
{
    /*if(!workingStatusUpdate.init)
    {
        workingStatusUpdate.init = true;
        function err(req, errorTypeStr) {
            if(errorTypeStr==="timeout"){
                // timed out - ok try again
                wsu.text("Timed out!");
                update();
            } else {
                wsu.text("Error: network connection error - status unknown.");
                setTimeout(update, 5000);
            }
        }
        jQ.ajaxSetup({timeout:6100, "error":err});
    }*/
    var request = null;
    var wsu = jQ("div.workingStatus");
    //if(wsu.hasClass("update"))
    if (true)
    {
        //wsu = wsu.filter(".update");
        function callback(data, statusCode)
        {
        	if (typeof(data.text)!="undefined") {
	            if(wsu.text) wsu.text(data.text);
	            if(wsu.html) wsu.html(data.html);
	            if(data.next) setTimeout(update, data.next);
	            else {
	                function updateCallback(data)       // finishedCallback
	                {
	                    //wsu.parent(".app-file-manager").replaceWith(data);
	                    jQ(".app-file-manager").replaceWith(data);
	                    try {
	                        xForm = getXForm();
	                    } catch(e) {
	                    }
	                    addBehaviours();
	                    zebraTables();
	                }
	                if(typeof(finishedCallback)!="function") {
	                    finishedCallback = updateCallback;
	                }
	                
	                request = jQ.post(getDocumentURI(), params={ajx:1, func:"fileManager"}, finishedCallback);
	            }
	        } 
        }
        function update()
        {	
            request = jQ.post(getDocumentURI(), params={ajax:"workingStatusUpdate"}, callback, "json");
        }
        setTimeout(update, 2000);
    }
}

function xFormAjaxSubmit(action, value, callback, actSubType)
{
  if(typeof(xForm)=="undefined" || xForm==null)
  {
    alert("no xForm");
    return;
  }
  if(typeof(actSubType)=="undefined") actSubType="";
  var postCount = xForm.postCount.value*1+1;
  xForm.postCount.value = postCount
  xForm.actType.value = action;
  xForm.actSubType.value = actSubType;
  value = escape(value);
  var qStr = "?func=file_manager&ispostback=1&ajx=1&postCount="+postCount+"&actType="+action+"&actData="+value+"&actSubType="+actSubType
  var url = xForm.action + qStr;
  var args = {"selected":getSelectedIds(),"all":jQ("#selectAll").attr("checked")?"true":""};
  jQ.post(url, args, callback);
}

function getSelectedIds()
{
  return jQ.map(jQ(".selected input.select, .alt-selected input.select"), function(x){return x.value;});
}



// =======================================
// TAGS
// =======================================

function tags()
{
  var d = jQ("div.ice-tags");
  d.find("div.ice-taggedwith span:first").click(taggedWith1stClick);
  d.find("div.ice-mytags").hide();
}

function taggedWith1stClick(e)
{
  var d = jQ("div.ice-tags");
  var taggedwith = d.find("div.ice-taggedwith")
  var mytags = d.find("div.ice-mytags")
  var toggle = function(e) { taggedwith.toggle(); mytags.toggle(); }
  mytags.find(".mytags").click(toggle);
  jQ(this).unbind().click(toggle);
  toggle();
  // add behaviour to 'myTags'
  var textInput = mytags.find("input[@type='text']");
  var addRemoveTag = function(e) { 
	var tag=jQ(this).text();
	var tags=textInput.val().split(/\s+/);
	var found=false;
	for(i=0; i<tags.length; i++)
	{
	   if(tag.toLowerCase()==tags[i].toLowerCase())
	   { found=true; tags[i]=null;}
	}
	if(found==false) tags[tags.length] = tag;
	tags = jQ.map(tags, function(x){return x;})
	textInput.val(tags.join(" "));
    return false;
  }
  mytags.find(".mytag").click(addRemoveTag);
}


// =======================================
// Show / Hide
// =======================================

function showHide()
{
    var showHides = jQ("fieldset.showHide");
    for(var x=0; x<showHides.size(); x++)
    {
        showHide = showHides.eq(x);
        legend = showHide.children("legend");
        legendText = legend.text();
        legend.html("Hide " + legendText);
        legend.css("cursor", "pointer");
        legend.css("color", "blue");
        //div = showHide.children("div")
        show = jQ("<span style='cursor:pointer;color:blue;padding-left:1ex;'>Show " + legendText + "</span>");
        showHide.wrap("<div/>");
        showHide.before(show);
        showHide.hide();
        function showFunc(event)
        {
            target = jQ(event.target);
            target.hide();
            target.next().show();
        }
        function hideFunc(event)
        {
            target = jQ(event.target).parent();
            target.hide();
            target.prev().show();
        }
        show.click(showFunc);
        legend.click(hideFunc);
    }
    showHides = jQ("div.showHideToggle");
    showHides.each(function() {
        var showHideDiv = jQ(this);
        var toggleText = showHideDiv.find("input[@name='toggleText']").val();
        var contentDiv = showHideDiv.find(">div");
        var cmd = showHideDiv.find(">span.command");
        cmd.click(function(){ contentDiv.toggleClass("hidden"); var t=cmd.html(); cmd.html(toggleText); toggleText=t; });
    });
}


// =======================================
// Description
// =======================================

function description()
{
    d = jQ(".content-description").parent()
    editDiv = jQ("<div style='text-align:right'></div>")
    edit = jQ("<span style='cursor:pointer;color:blue;'>edit </span>")
    edit.click(descriptionEditClick)
    editDiv.append(edit)
    d.append(editDiv)
}

function descriptionEditClick(event)
{
    //target = jQ(event.target)
    desc = jQ(".content-description")
    desc.hide()
    desc.nextAll().hide()
    
    ta = jQ("<div class='content-description-edit'><textarea cols='80'>" + desc.html() + "</textarea></div>")
    cancel = jQ("<button>cancel</button>")
    cancel.click(descriptionCancelClick)
    submit = jQ("<button>submit</button>")
    submit.click(descriptionSubmitClick)
    ta.append(cancel)
    ta.append(submit)
    desc.parent().append(ta)
}

function descriptionCancelClick(event)
{
    d = jQ(".content-description-edit")
    d.remove()
    d = jQ(".content-description")
    d.parent().children().show()
}

function descriptionSubmitClick(event)
{
    d = jQ(".content-description-edit")
    desc = d.find("textarea").attr("value")
    d.remove()
    d = jQ(".content-description")
    d.html(desc)
    d.parent().children().show()
}


function oscar()
{
    var uri = getDocumentURI();
    var files = uri.substring(uri.lastIndexOf("/")+1);
    var image = jQ("img.sci").hide();
    var sciLegend = jQ("div.sci-legend");
    var appletHtml = "<div style='text-align: center; left:0px; padding:8px;'><applet name='Jmol' code='JmolApplet' archive='JmolApplet.jar' height='300' width='300'><param name='load' value='files/cml.xml'><param name='progressbar' value='true'><param name='progresscolor' value='blue'></applet></div>";
    var sciDialog = jQ("#sci-dialog");

    files = files.substring(0, files.lastIndexOf("."));
    files += "_files/";
    //var oscarUri = "http://localhost:8181";
    var oscarUri = "?ajax=1&func=oscar&";
    if (sciDialog.size()>0) {
        jQ("head").append("<script type='text/javascript' src='/skin/jquery-ui.js'><!-- --></script>");
    }
    sciLegend.append("<div class='sciImgDiv' style='display:none;border:1px solid #8080FF;position:absolute;'>IMG</div>");
    var sciImgDiv = sciLegend.find("div.sciImgDiv");

    var getNeViewerUri = function(d) {
        var args = [];
        var d2 = {"name":d["surface"], "type":d["type"], "smiles":d["SMILES"], "inchi":d["InChI"], "ontids":d["ontIDs"] }
        for(k in d2) {
            var v = encodeURIComponent(d2[k])
            if(v!="undefined") args.push(k.toLowerCase() + "=" + v);
        }
        //return "./NEViewer?" + args.join("&");
        return oscarUri + args.join("&");
    }

    var showDialog = function(e) {
        var jx=jQ(e.target); 
        var d = getMyDict(jx);
        var cml = d["cmlRef"]
        var imgUri = view(d);
        try {
          sciDialog.dialog({modal:true, width:"680px", height:"600px", resizable:true, draggable:true, 
                overlay:{opacity:0.5, background:"black"}, "title":""});
          var html = "<div style='float:right;padding-right:1em;'><span class='command close'>Close</span></div>";
          if(imgUri.indexOf("blank=")==-1)  html += "<div style='float:left;padding:1em;'><img src='"+imgUri+"' /></div>";
          if (d["SMILES"]!=null) html += appletHtml.replace("files/cml.xml", files+cml+".cml");
          else html += "<div style='clear:left;'>&#160;</div>"
          html += "<div class='NEView' style='padding:1em;'><img src='/skin/loading.gif' /></div>";
          sciDialog.html(html);
          var neView = sciDialog.find("div.NEView").load(getNeViewerUri(d));
          sciDialog.append("<div style='float:right;padding-right:1em;'><span class='command close'>Close</span></div>");
          sciDialog.find("span.close").click(function(){sciDialog.dialog("close");});
          sciDialog.css("overflow", "auto");  // or scroll
          sciDialog.show();
        } catch(e) { alert(e.message); }
    }
    var inHover = false;
    var hoverImage = function(e) {
        var jx=jQ(e.target); 
        var d = getMyDict(jx);
        var imgUri;
        try {
          imgUri = view(d);
          sciImgDiv.html("<img src='" + imgUri + "' />");
          sciImgDiv.css("top", e.pageY+15);
          var db = jQ("body");
          var w = parseInt(db.css("width"));
          var x = e.pageX;
          if (x<20) x=20; else if ((x+340)>w) x=w-340;
          sciImgDiv.css("left", x);
          sciImgDiv.show();
        } catch(e) { alert(e.message); }
        inHover = true;
    }
    var closeDialog = function() { sciDialog.dialog("close"); inHover=false; }
    var setImage = function(x) { 
        var imgUri = view(getMyDict(x));
        image.attr("src", imgUri);
    }

    var getImageUri = function(n, v) {
        return oscarUri + "img=1&" + n + "=" + encodeURIComponent(v);
    }
    var view = function(x) {    // x = dict
         if(x["InChI"] != null && x["SMILES"] != null) {
            return getImageUri("inchi", x["InChI"]);
            //"&smiles=" + encodeURIComponent(x["SMILES"]));		    
    	 } else if(x["InChI"] != null) {
            return getImageUri("inchi", x["InChI"]);
		 } else if(x["SMILES"] != null) {
            return getImageUri("smiles", x["SMILES"]);
		 } else if(x["Element"] != null) {
             return getImageUri("element", x["Element"]);
		 } else {
            return getImageUri("blank", "");
		 }
    }
    var getMyDict = function(jx) {
        var a = jx.attr("title").split("; ");
        var d = {};
        var i;
        for(i=0; i<a.length; i++)
        {
            var x = a[i];
            var p = x.split(" = ");
            d[p[0]] = p[1];
        }
        return d;
    }

    var sci = jQ("span.sci[@title]");
    sci.each(function(count, s) 
        {   s = jQ(s); 
            var d = getMyDict(s);
            if (d["SMILES"]!=null)
            {
                s.attr("style", "text-decoration: underline;");                
                //s.hover(function(x){ var jx=jQ(x.target); setImage(jx); }, function(){});
                s.hover(function(e){ hoverImage(e); }, function(){sciImgDiv.hide();} );
            }
            s.click(function(e){ showDialog(e); });
            s.css("cursor", "pointer");
        } 
    );
}


// =======================================
// Utils
// =======================================


function print(arg)
{
    alert(arg);
}

function test()
{
    print ("test() - Testing");
}

function now() {
  var d = new Date();
  return d.getTime();
}

function gotoURI(uri) 
{
    window.location=uri;
}

function getDocumentURI()
{
    var uri = document.documentURI;
    if(typeof(uri)=="undefined") uri=window.location+"";
    return uri;
}

function stripString (stringVal) {
	var newStr = "";
	for (var i=0; i<stringVal.length; i++) {
		if (stringVal.charCodeAt(i) != 32) {
			newStr += stringVal[i];
		}
	}
	return newStr;
}


function zebraTables()
{
  try
  {
    jQ("table.zebra tr:even:gt(0)").addClass("alt");
  }
  catch(e)
  {
  }
}


function hideBody() { jQ("div.body").hide(); hideVisibleAnnotations(); }
function showBody() { jQ("div.body").show(); showVisibleAnnotations(); }


function readCookie(name, _default) 
{
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++)
	{
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return _default;
}
function setCookie(name, value)
{
 	document.cookie = name.toString() + "=" + value.toString() + ";"
}
function deleteCookie(name)
{
    document.cookie = name.toString() + "=; expires Thu, 1 Jan 1970 12:00:00 UTC;"
}


function xFormSubmit(action, value, subType)
{
  if(typeof(xForm)=="undefined" || xForm==null)
  {
    alert("no xForm");
    return;
  }
  if(typeof(action)=="undefined") action="";
  if(typeof(value)=="undefined") value="";
  if(typeof(subType)=="undefined") subType="";
  xForm.postCount.value = xForm.postCount.value*1+1; 
  xForm.actType.value = action;
  xForm.actData.value = value;
  xForm.actSubType.value = subType;
  xForm.submit();
}

function getXForm() {
    var form = jQ("form#formX:eq(0)");
    if(form.size()==0) form = jQ("form#formXT:eq(0)");
    if(form.size()>0) xForm = form[0];
    else if(typeof(xForm)=="undefined") xForm = null;
    return xForm;
}

function refresh() { window.location = window.location; } 


function gotoQueryStringLocation()
{
  var linkText = getParamValue("linkText");
  if (linkText != null) { 
	  linkText = unescape(linkText)
	  if (linkText.indexOf(" and ")>-1){
		var linkTextSplit = linkText.split("and");
		linkText = linkTextSplit[0];
	  }
	  linkText = stripString(linkText); 
	  var linkHref = getParamValue("linkHref");
	  //alert ('linkHref: ' + linkHref);
	  var links = jQ("div.body")
	
	  if (linkHref != null) {
		  links.find("a").each( function(i) {
			var s = jQ(this);
			var attrVal = s.attr("href");
			//invalidlinkText = '"' + s.text() + '"';
			invalidlinkText = '"' + s.html() + '"';
			invalidlinkText = stripString(invalidlinkText);
			
			/* get the last part of linkHref as ice might convert the link to relative path */
			if (linkHref != "") {
				var index = linkHref.indexOf("/")
				if (index > -1) {
					var strQry = linkHref.split("/");
					var len = strQry.length - 1;
					linkHref = strQry[len];
					//linkHref = unescape(linkHref);
				}
			}
			var found = false;
			if ((invalidlinkText == linkText )  || (invalidlinkText.indexOf(linkText)>-1)) {
				found = true;
			}
			
			if (found && attrVal.indexOf(linkHref)>-1) {
				anchor = jQ("<a name='badLink'/>");
				s.append(anchor);
				window.location.href = "#badLink";
			}
		  });
	   }
	}
	else {
		//Just get the bookmark if exist
		var location = window.location.href;
		if ( location.indexOf("#") > -1) {
			bookmark = location.substr(location.indexOf("#")+1);
			bookmarkVal = '"<!--' + bookmark + '-->"';
			var links = jQ("div.body");
			links.find("a").each( function(i) {
				var s = jQ(this);
				var attrVal = s.attr("href");
				linkText = '"' + s.html() + '"';
				linkText = stripString(linkText);
				if (bookmarkVal == linkText) {
					window.location.href = "#" + bookmark;
				}
			});
		}
	}
}

function getParamValue (paramName) {
	var cmpstring = paramName + "=";
	var cmplen = cmpstring.length;
	var location = window.location.href;
	if ( location.indexOf("?") > -1) {
		var strQry = location.substr(location.indexOf("?")+1);
		var arr    = strQry.split("&");
		for (var i=0; i<arr.length; i++) {
			if (arr[i].substr(0,cmplen)==cmpstring) {
				//get the first '=' sign
				index = arr[i].indexOf("=");
				var len = arr[i].length;
				var paramPair = arr[i].slice(index+1, len);
				return paramPair;
				break;
			} 

		}
	}

}


function IceTimer(callbackFunc, interval, number)
{
    var timerId=null;
    if (number == undefined) number = -1;
    function setTimer()
    {
        if (number!=0)
        {
            timerId = setTimeout(tic, interval)
            number -= 1;
        }
    }
    function tic()
    {
        timerId = null
        callbackFunc()
        setTimer()
    }
    function cancel()
    {
        number = 0
        clearTimeout(timerId)
    }
    this.cancel = cancel
    this.interval = interval
    this.callback = callbackFunc
    setTimer()
    function getNumber()
    {
        if (timerId==null)
            return number;
        else
            return number+1;
    }
    this.getNumber = getNumber
}

function map(func, list) {
    rList = []
    for(x=0; x<list.length; x++) {
        rList.push(func(list[x]));
    }
    return rList;
}


// =======================================
// Crc32
// =======================================

function Hex32(val)
{
  var n;
  var str1;
  var str2;

  n=val&0xFFFF;
  str1=n.toString(16).toUpperCase();
  while (str1.length<4)
  {
    str1="0"+str1;
  }
  n=(val>>>16)&0xFFFF;
  str2=n.toString(16).toUpperCase();
  while (str2.length<4)
  {
    str2="0"+str2;
  }
  return str2+str1;
}

function Crc32Hex(str)
{
  return Hex32(Crc32Str(str));
}

function Crc32Str(str)
{
  var len = str.length;
  var crc = 0xFFFFFFFF;
  for(var n=0; n<len; n++)
  {
    crc = Crc32Add(crc, str.charCodeAt(n));
  }
  return crc^0xFFFFFFFF;
}

var Crc32Tab = [
    0x00000000,0x77073096,0xEE0E612C,0x990951BA,0x076DC419,0x706AF48F,0xE963A535,0x9E6495A3,
    0x0EDB8832,0x79DCB8A4,0xE0D5E91E,0x97D2D988,0x09B64C2B,0x7EB17CBD,0xE7B82D07,0x90BF1D91,
    0x1DB71064,0x6AB020F2,0xF3B97148,0x84BE41DE,0x1ADAD47D,0x6DDDE4EB,0xF4D4B551,0x83D385C7,
    0x136C9856,0x646BA8C0,0xFD62F97A,0x8A65C9EC,0x14015C4F,0x63066CD9,0xFA0F3D63,0x8D080DF5,
    0x3B6E20C8,0x4C69105E,0xD56041E4,0xA2677172,0x3C03E4D1,0x4B04D447,0xD20D85FD,0xA50AB56B,
    0x35B5A8FA,0x42B2986C,0xDBBBC9D6,0xACBCF940,0x32D86CE3,0x45DF5C75,0xDCD60DCF,0xABD13D59,
    0x26D930AC,0x51DE003A,0xC8D75180,0xBFD06116,0x21B4F4B5,0x56B3C423,0xCFBA9599,0xB8BDA50F,
    0x2802B89E,0x5F058808,0xC60CD9B2,0xB10BE924,0x2F6F7C87,0x58684C11,0xC1611DAB,0xB6662D3D,
    0x76DC4190,0x01DB7106,0x98D220BC,0xEFD5102A,0x71B18589,0x06B6B51F,0x9FBFE4A5,0xE8B8D433,
    0x7807C9A2,0x0F00F934,0x9609A88E,0xE10E9818,0x7F6A0DBB,0x086D3D2D,0x91646C97,0xE6635C01,
    0x6B6B51F4,0x1C6C6162,0x856530D8,0xF262004E,0x6C0695ED,0x1B01A57B,0x8208F4C1,0xF50FC457,
    0x65B0D9C6,0x12B7E950,0x8BBEB8EA,0xFCB9887C,0x62DD1DDF,0x15DA2D49,0x8CD37CF3,0xFBD44C65,
    0x4DB26158,0x3AB551CE,0xA3BC0074,0xD4BB30E2,0x4ADFA541,0x3DD895D7,0xA4D1C46D,0xD3D6F4FB,
    0x4369E96A,0x346ED9FC,0xAD678846,0xDA60B8D0,0x44042D73,0x33031DE5,0xAA0A4C5F,0xDD0D7CC9,
    0x5005713C,0x270241AA,0xBE0B1010,0xC90C2086,0x5768B525,0x206F85B3,0xB966D409,0xCE61E49F,
    0x5EDEF90E,0x29D9C998,0xB0D09822,0xC7D7A8B4,0x59B33D17,0x2EB40D81,0xB7BD5C3B,0xC0BA6CAD,
    0xEDB88320,0x9ABFB3B6,0x03B6E20C,0x74B1D29A,0xEAD54739,0x9DD277AF,0x04DB2615,0x73DC1683,
    0xE3630B12,0x94643B84,0x0D6D6A3E,0x7A6A5AA8,0xE40ECF0B,0x9309FF9D,0x0A00AE27,0x7D079EB1,
    0xF00F9344,0x8708A3D2,0x1E01F268,0x6906C2FE,0xF762575D,0x806567CB,0x196C3671,0x6E6B06E7,
    0xFED41B76,0x89D32BE0,0x10DA7A5A,0x67DD4ACC,0xF9B9DF6F,0x8EBEEFF9,0x17B7BE43,0x60B08ED5,
    0xD6D6A3E8,0xA1D1937E,0x38D8C2C4,0x4FDFF252,0xD1BB67F1,0xA6BC5767,0x3FB506DD,0x48B2364B,
    0xD80D2BDA,0xAF0A1B4C,0x36034AF6,0x41047A60,0xDF60EFC3,0xA867DF55,0x316E8EEF,0x4669BE79,
    0xCB61B38C,0xBC66831A,0x256FD2A0,0x5268E236,0xCC0C7795,0xBB0B4703,0x220216B9,0x5505262F,
    0xC5BA3BBE,0xB2BD0B28,0x2BB45A92,0x5CB36A04,0xC2D7FFA7,0xB5D0CF31,0x2CD99E8B,0x5BDEAE1D,
    0x9B64C2B0,0xEC63F226,0x756AA39C,0x026D930A,0x9C0906A9,0xEB0E363F,0x72076785,0x05005713,
    0x95BF4A82,0xE2B87A14,0x7BB12BAE,0x0CB61B38,0x92D28E9B,0xE5D5BE0D,0x7CDCEFB7,0x0BDBDF21,
    0x86D3D2D4,0xF1D4E242,0x68DDB3F8,0x1FDA836E,0x81BE16CD,0xF6B9265B,0x6FB077E1,0x18B74777,
    0x88085AE6,0xFF0F6A70,0x66063BCA,0x11010B5C,0x8F659EFF,0xF862AE69,0x616BFFD3,0x166CCF45,
    0xA00AE278,0xD70DD2EE,0x4E048354,0x3903B3C2,0xA7672661,0xD06016F7,0x4969474D,0x3E6E77DB,
    0xAED16A4A,0xD9D65ADC,0x40DF0B66,0x37D83BF0,0xA9BCAE53,0xDEBB9EC5,0x47B2CF7F,0x30B5FFE9,
    0xBDBDF21C,0xCABAC28A,0x53B39330,0x24B4A3A6,0xBAD03605,0xCDD70693,0x54DE5729,0x23D967BF,
    0xB3667A2E,0xC4614AB8,0x5D681B02,0x2A6F2B94,0xB40BBE37,0xC30C8EA1,0x5A05DF1B,0x2D02EF8D];
function Crc32Add(crc, c)
{
  return Crc32Tab[(crc^c)&0xFF]^((crc>>8)&0xFFFFFF);
}

// =======================================
// Annotating  annotea TESTING
// =======================================

function enableParaAnnotating_Danno()
{
    //
    //return;     // off for now
    // High para
    var annotations = {}
    var annotationComments = {}
    var bodyDiv = jQ("div.body > div:first");
    var last = null;
    var annotateDiv = "<div class='annotate-form' style='background-color: transparent;'><textarea cols='80' rows='8'></textarea><br/>";
    annotateDiv += "<button class='cancel'>Cancel</button>&#160;"
    annotateDiv += "<button class='submit'>Submit</button> <span class='info'></span>"
    annotateDiv += "</div>";
    annotateDiv = jQ(annotateDiv);
    var textArea = annotateDiv.find("textarea");
    var unWrapLast = function() { if(last!=null){last.parent().replaceWith(last); last=null;} }
    //
    var decorateAnnotation = function(anno) {
        var d;
        if (anno.hasClass("closed")) d = jQ("<span>&#160; <span class='delete-annotate command'> Delete</span></span>");
        else d = jQ("<span>&#160;<span class='close-annotate command'>Close</span>&#160;<span class='annotate-this command'>Reply</span></span>");
        anno.find("div.anno-info:first").append(d);
        var deleteClick = function(e) {
            var id = anno.attr("id");
            jQ.post(window.location+"?", {ajax:"annotea", id:id, method:"delete"},
                 function(rt){if(rt=="Deleted") {anno.remove(); } }, "text");
        }
        var closeClick = function(e) {
            var id = anno.attr("id");
            var callback = function(responseText, statusCode) {
                var updatedAnno = jQ(responseText);
                decorateAnnotation(updatedAnno);
                anno.replaceWith(updatedAnno);
                updatedAnno.find("div.inline-annotation").each(function(c){ var anno=jQ(this); decorateAnnotation(anno); });
            }
            jQ.post(window.location+"?", {ajax:"annotea", id:id, method:"close"},
                callback, "text");
        }
        var replyClick = function(e) {
            var id = anno.attr("id");
            annotate(anno);
        }
        d.find("span.close-annotate").click(closeClick);
        d.find("span.annotate-this").click(replyClick);
        d.find("span.delete-annotate").click(deleteClick);
    }
    //
    var annotate = function(me) {
            if(last!=null) { annotateDiv.find("button.close").click(); unWrapLast(); }
            var id = me.attr("id");
            if(typeof(id)=="undefined") { return; }
            var closeClick = function() { annotationComments[id] = jQ.trim(textArea.val()); unWrapLast(); }
            var submitClick = function() {
                unWrapLast();
                annotationComments[id] = "";
                var url = window.location;
                var text = jQ.trim(textArea.val());
                if(text=="") return;
                var html = me.wrap("<div/>").parent().html();    // Hack to access the outerHTML
                me.parent().replaceWith(me);
                var d = {ajax:"annotea", paraId:id,
                        html:html, text:text, method:"add" };
                var callback = function(responseText, statusCode) {
                    jQ.get("", {"ajax":"annotea", "method":"getAnnos", "url":responseText}, callback_j, "json");
                }
                selfUrl = me.find("input[name='selfUrl']").val() || "";
                rootUrl = me.find("input[name='rootUrl']").val() || "";
                d["inReplyToUrl"] = selfUrl;
                d["rootUrl"] = rootUrl;
                url += "?"          // work around a jQuery bug
                jQ.post(url, d, callback, "text");
            }
            var restore = function() {
                if(id in annotationComments) {textArea.val(annotationComments[id]);} else {textArea.val("");}
            }
            restore();
            // wrap it
            me.wrap("<div class='inline-annotation-form'/>");
            me.parent().append(annotateDiv);
            annotateDiv.find("button.clear").click(function(){textArea.val("");});
            annotateDiv.find("button.cancel").click(function(){textArea.val(annotationComments[id]); closeClick();});
            annotateDiv.find("button.close").click(closeClick);
            annotateDiv.find("button.submit").click(submitClick);
            me.parent().prepend("<div class='app-label'>Comment on this:</div>");
            unWrapLast();
            last = me;
            textArea.focus();
    }
    
    //
    var click = function(e) {
        var t = e.target;
        var me = jQ(t).parent();
        var name = me[0].tagName;
        if (name=="P" || name=="DIV" || name.substring(0,1)=="H"){
            removePilcrow();
            // me
            annotate(me);
        } else {
            alert(name);
        }
        return false;
    }
    //
    var getSelectedText = function(){
        if(window.getSelection) return window.getSelection();
        if(document.getSelection) return document.getSelection();
        if(document.selection) return document.selection.createRange().text;
        return "";
    }

    var pilcrowSpan = jQ("<span class='pilcrow command'> &#xb6;</span>");
    var prTimer = 0;
    var addPilcrow = function(jqe) { if(prTimer)clearTimeout(prTimer); jqe.append(pilcrowSpan);
                                        pilcrowSpan.unbind(); pilcrowSpan.click(click);
                                        pilcrowSpan.mousedown(function(e){ return false; });
                                        pilcrowSpan.mouseup(click);     // for I.E.
                                   }
    var removePilcrow = function() { prTimer=setTimeout(function(){prTimer=0; pilcrowSpan.remove();}, 100); }
    bodyDiv.mouseover(function(e) {
        var t = e.target;
        var name = t.tagName;
        if(name!="P" && name.substring(0,1)!="H") { if(t.parentNode.tagName=="P") t=t.parentNode; else return;}
        {
            var me = jQ(t);
            if(me.html()=="") return;
            me.unbind();
            me.mouseover(function(e) { if(getSelectedText()=="") addPilcrow(me); return false;} );
            me.mouseout(function(e) { removePilcrow(); } );
            me.mousedown(function(e) { removePilcrow(); } );
            me.mouseover();
        }
    });

    // enable annotations for the Title as well
    var titles = jQ("div.title");
    var title1 = titles.filter(":eq(0)");
    var title2 = titles.filter(":eq(1)");
    var titleId = title2.attr("id");
    if(typeof(titleId)=="undefined") titleId="h_titleIdt";
    titleId = titleId.toLowerCase();
    title2.attr("id", "_" + titleId);
    title1.attr("id", titleId);
    title1.mouseover(function(e) {
        var pilcrow = jQ("<span class='pilcrow command'> &#xb6;</span>");
        var me = jQ(e.target);
        me.unbind();

        me.mouseover(function(e) { if(getSelectedText()=="") addPilcrow(me); return false;} );
        me.mouseout(function(e) { removePilcrow(); } );
        me.mousedown(function(e) { removePilcrow(); } );
        me.mouseover();
    });
    //
    var commentOnThis = jQ("div.annotateThis");
    commentOnThis.find("span").addClass("command");
    commentOnThis.find("span").click(click);
    function hideShowAnnotations() {
        var me = jQ(this);
        var text = me.text();
        var inlineAnnotations = jQ("div.inline-annotation");
        var l = inlineAnnotations.size();
        var h = inlineAnnotations.filter(".closed").size();
        if(text.substring(0,1)=="H") {
            me.text("Show comments ("+(l-h)+" opened, "+h+" closed)");
            inlineAnnotations.hide();
        }
        else {
            me.text("Hide comments ("+(l-h)+" opened, "+h+" closed)");
            inlineAnnotations.show();
        }
    }

    jQ("div.ice-toolbar .hideShowAnnotations").click(hideShowAnnotations).text("S").click();
    
    var attachAnnotation = function(anno, para) {
        if(typeof(para)!="undefined" && para.size()>0) {
            if(para.hasClass("inline-annotation")) {
                para.find(">div.anno-children").prepend(anno);
            } else {
                if(!para.parent().hasClass("inline-anno")) {
                    para.wrap("<div class='inline-anno'/>");
                }
                para.after(anno);
                para.css("margin", "0px");
            }
        }
    }
    //
    // Show inline annotations
    //
    
    function positionAndDisplay(inlineAnnotation){
        var me = jQ(inlineAnnotation);
        // add close and reply buttons
        //decorateAnnotation(me.find("div.inline-annotation").andSelf()); // and children
        decorateAnnotation(me); 
        var parentId = me.find("input[@name='parentId']").val();
        var p = bodyDiv.find("#" + parentId);
        if(parentId in annotations) p = annotations[parentId];
        if(parentId==titleId) p = title1;
        if(p.size()==0) {       // if orphan
            me.find("div.orig-content").show();
            bodyDiv.append(me);
        }
        attachAnnotation(me, p);
        var id = me.attr("id");
        annotations[id] = me;
    }

    if(true) {
        var createAnnoDiv = function(d, callback){
            var s = "<div class='inline-annotation' id='" + d.selfUrl + "'>"
            s += "<input name='parentId' value='" + d.annotates + "' type='hidden'><!-- --></input>";
            s += "<input name='rootUrl' value='" + d.rootUrl + "' type='hidden'><!-- --></input>";
            s += "<input name='selfUrl' value='" + d.selfUrl + "' type='hidden'><!-- --></input>";
            s += " <div class='orig-content' style='display:none;'> </div>";
            s += " <div class='anno-info'>Comment by: <span>" + d.creator + "</span>";
            s += " &nbsp; <span>" + d.created + "</span></div>";
            s += " <div class='anno-children'><!-- --></div>";
            s += "</div>";
            var div = jQ(s);
            // Get and add the comment text(body)
            jQ.get("", {ajax:"annotea", method:"get", url: d.bodyUrl},
                function(data) {div.find(">div:last").before(jQ(data).text());});
            // If we are a root annotation get any/all of our children (replies)
            if(d.rootUrl==d.selfUrl){
                var rUrl = "?w3c_reply_tree=" + escape(d.rootUrl);
                jQ.get("", {ajax:"annotea", method:"getAnnos", url: rUrl}, callback, "json");
            }
            return div;
        }
        function callback_j(dList){
            //selfUrl, bodyUrl, rootUrl, inReplyToUrl, annotates, creator, created
            if(typeof(dList)=="string") { alert("string and not a list"); return;}
            jQ.each(dList, function(c, d){
                var div = createAnnoDiv(d, callback_j);
                positionAndDisplay(div);
            });
        }
//        function callback_t(data){
//            jQ.each(data.firstChild.childNodes, function(c, x) {
//                if(x.localName=="Description") {
//                    var creator = ""; var created = "";
//                    var id = ""; var bodyUrl = ""; var selfUrl = "";
//                    var rootUrl = ""; inReplyToUrl = "";
//                    selfUrl = jQ(x).attr("rdf:about");
//                    jQ.each(x.childNodes, function(cc, n){
//                        var lName = n.localName;
//                        if(lName=="creator"){
//                            creator = n.textContent;
//                        } else if(lName=="created") {
//                            created = n.textContent;
//                        } else if(lName=="context"){
//                            var xp = n.textContent.split("#")[1]
//                            id = xp.split('id("')[1].split('")')[0]
//                        } else if(lName=="body"){
//                            bodyUrl = jQ(n).attr("rdf:resource");
//                        } else if(lName=="root"){
//                            rootUrl = jQ(n).attr("rdf:resource");
//                        } else if(lName=="inReplyTo"){
//                            inReplyToUrl = jQ(n).attr("rdf:resource");
//                        }
//                    });
//                    if(inReplyToUrl!="") id = inReplyToUrl;
//                    if(rootUrl=="") rootUrl = selfUrl;
//
//                    var createAnnoDiv = function(){
//                        var d = "<div class='inline-annotation' id='" + selfUrl + "'>"
//                        d += "<input name='parentId' value='" + id + "' type='hidden'><!-- --></input>";
//                        d += "<input name='rootUrl' value='" + rootUrl + "' type='hidden'><!-- --></input>";
//                        d += "<input name='selfUrl' value='" + selfUrl + "' type='hidden'><!-- --></input>";
//                        d += " <div class='orig-content' style='display:none;'> </div>";
//                        d += " <div class='anno-info'>Comment by: <span>" + creator + "</span> &nbsp; <span>" + created + "</span></div>";
//                        d += " <div class='anno-children'><!-- --></div>";
//                        d += "</div>";
//                        d = jQ(d);
//                        // Get and add the comment text(body)
//                        jQ.get("", {ajax:"annotea", method:"get", url: bodyUrl},
//                            function(data) {d.find(">div:last").before(jQ(data).text());});
//                        // If we are a root annotation get any/all of our children (replies)
//                        if(rootUrl==selfUrl){
//                            rUrl = "?w3c_reply_tree=" + escape(rootUrl);
//                            jQ.get("", {ajax:"annotea", method:"get", url: rUrl}, callback_t);
//                        }
//                        return d;
//                    }
//                    d = createAnnoDiv();
//                    positionAndDisplay(d);
//                }
//            });
//        }
        var query = "?w3c_annotates=" + escape(window.location);
        //jQ.get("x", {ajax:"annotea", method:"get", url:query}, callback_t);
        jQ.get("x", {ajax:"annotea", method:"getAnnos", url:query}, callback_j, "json");
    }
}

/* The End */












