

function editConfig(jQ){
    var dialog = jQ("#dialog");
    var accord = jQ(".accordion:first").html();

    var configData=null, configDataBackup=null;
    var iceHost=jQ("#iceHost");
    var icePort=jQ("#icePort");
    var oooPath=jQ("#oooPath"), oooPathFeedback=jQ("#oooPathFeedback"), oooPathCell=jQ("#oooPathCell");
    var oooPort=jQ("#oooPort");
    var homePath=jQ("#homePath");
    var versionInfo=jQ("#versionInfo");
    var commonSettings={};

    var gSettings=jQ(".defaultSettings .settings");     // <table class='settings'>
    // clean clone for IE
    var settingsTemp=jQ("<table class='settings'>" + gSettings.html() + "</table>");

    
    function getIndexOf(arr, item){
        if(Array.prototype.indexOf){
            return arr.indexOf(item);
        }else{
            for(var i in arr){ if(arr[i]===item) return i;}
            return -1;
        }
    }

    function trim(s){
        return s.replace(/^\s+|\s+$/g, "")
    }

    function ajax(func, args, callback){
        if (typeof(callback)==="undefined") callback = function(data) {
            if("error" in data) alert(data.error);
        }
        if (typeof(args)==="undefined") args={};
        args["ajax"]="config2Edit";
        args["func"]=func;
        //jQ.getJSON("editconfig", args, callback);
        jQ.post("editconfig", args, callback, "json");
    }

    function loadData(data){
        try{
            configData = data;
            configDataBackup = jQ.extend(true, {}, data);
            versionInfo.html(data.versionInfo);
            homePath.text(data.homePath);
            iceHost.val(data.hostAddress).change(function(){
                var e=jQ(this);
                data.hostAddress = e.val();
            });
            icePort.val(data.port).change(function(){
                var e=jQ(this);
                data.port = e.val();
            });
            oooPort.val(data.settings.oooPort.value).change(function(){
                var e=jQ(this);
                data.settings.oooPort.value = e.val();
            });
            oooPath.val(data.settings.oooPath.value).change(function(){
                var e=jQ(this);
                data.settings.oooPath.value = e.val();
            });
            loadSettingsData(gSettings, data.settings);
            addReps(data.repositories, data.settings.defaultRepositoryName.value);
        }catch(e){
           alert(e)
        }
    }

    function loadSettingsData(settings, data){
        var tbody = settings.find("tbody");
        var name;
        tbody.find("tr.setting").remove();
        var before = tbody.find(".addSetting")
        names = [];
        for(name in data) names.push(name);
        names.sort();
        for(var i in names){
            name = names[i];
            arr = ["oooHost", "oooPath","defaultRepositoryName",
                        "defaultDocumentTemplatesPath", "defaultExportPath",
                        "oooPythonPath", "oooPort", "webserver"];
            //if(arr.indexOf(name)!=-1) continue;
            if(getIndexOf(arr, name)!=-1) continue;
            var d = data[name];
            // d.value, d.type, d.desc
            var e = createSettingElement(name, d.value, d.type, d.desc, data);
            before.before(e);
        }

        var tr=tbody.find("tr.addSetting");
        var addSettingButton = tr.find("button:first");
        var table = tr.find("table");
        addSettingButton.unbind().click(function(){
            addSettingButton.hide();
            table.find("input:first").val("");
            table.find("input:last").val("");
            table.show();
        });
        addSettingButton.siblings(".commonSettings").remove();
        var s = "<select class='commonSettings' style='display:block;'><option>Common settings </option></select>"
        s = jQ(s);
        var n;
        for(n in commonSettings){
            if(!data[n])  s.append("<option value='"+n+"'>" +n + "</option>")
        }
        s.change(function(){
            n = s.val();
            s.find("option[value='"+n+"']").remove();
            data[n] = {"name":n, "value":commonSettings[n].value,
                "type":commonSettings[n].type, "desc":commonSettings[n].desc};
            // IE 8 bug - do later step later as a work around for this IE 8 bug
            function later(){
              e = createSettingElement(n, data[n].value, data[n].type, data[n].desc, data);
              before.before(e);
            }
            setTimeout(later, 10);
        });
        addSettingButton.before(s);
        table.find(".cancelButton").unbind().click(function(){
            table.hide();
            addSettingButton.show();
        });
        table.find(".addVarButton").unbind().click(function(){
            name = trim(table.find("input:first").val());
            if(name==="") return;
            var varType = table.find("select:first").val();
            var varDesc = trim(table.find("input:last").val());

            if(data[name]){
                alert("A setting with this name already exists!");
                return;
            }
            data[name] = {"name":name, "value":"", "type":varType, "desc":varDesc};
            e = createSettingElement(name, "", varType, varDesc, data);
            before.before(e);

            table.find("input").val("");

            table.hide();
            addSettingButton.show();
        });
        table.hide();
    }

    function createSettingElement(name, value, type, desc, data){
        var e = jQ("<tr class='setting'><td>"+name+":</td><td class='data "+type+"' name='"+name+"'></td></tr>");
        var td2 = e.find("td.data");
        var s='', i;
        var delBut = " &#160;<button class='delete' title='remove this entry'>Delete</button>"
        // delBut += " <span class='desc'/>"

        if(type=="str"){
            s = "<input size='50' type='text' value=''/>" + delBut;
            s = jQ("<div>"+s+"</div>");
            i = s.find("input");
            i.val(value);
            i.change(function(){
                data[name].value=i.val().trim();
            });
            if(name=="defaultRepositoryName") i.attr("disabled", "disabled");
        }else if(type=="bool"){
            s = "<input type='checkbox'/>" + delBut;
            s = jQ("<div>"+s+"</div>");
            if(value=="True") s.find("input").attr("checked", "checked");
            i = s.find("input");
            i.change(function(){
                if(i.attr("checked")){
                    data[name].value="True";
                }else{
                    data[name].value="False";
                }
            });
        //}else if(type=="int"){
        }else if(type=="list"){
            s = "<input size='50' type='text' value='' disabled='disabled'/> " + delBut;
            s = jQ("<div>"+s+"</div>");
            s.find("input").val(value.slice(1,-1));
        }else{
            s = "type='"+type+"' not supported yet! ";
            s = jQ("<div>"+s+"</div>");
        }
        if(desc){
            //s.find(".desc").text("("+desc+")");
            s.prepend("<div class='desc' style='color:#6060FF;'>"+desc+"</div");
        }
        td2.append(s);
        arr = ["asServiceOnly", "enableExternalAccess", "includeSource",
            "server", "defaultRepositoryName"];
        //if(arr.indexOf(name)!=-1){
        if(getIndexOf(arr, name)!=-1){
            e.find(".delete").remove();
        }else{
            e.find(".delete").click(function(){
                e.remove();
                delete data[name];
            });
        }
        return e;
    }

    function addReps(repsData, defaultRepName){
        var name, repNames = [];
        for(name in repsData) repNames.push(name);
        repNames.sort();
        jQ(".rep:visible").remove();
        for(var i in repNames) addRep(repNames[i], repsData, defaultRepName);
        jQ("#addrep").parent().append(jQ("#addrep"));
    }

    function addRep(name, repsData, defaultRepName){
        //var rep = jQ("#rep_temp").clone().show();
        var rep = jQ( "<div class='rep'>"+jQ("#rep_temp").html()+"</div>");
        rep.attr("id", "rep_" + name);
        var data = repsData[name];
        if(typeof(data)==="undefined") {
            alert("Repository name '"+name+"' not found!");
        }
        var settingsNode = settingsTemp.clone();
        var isDefault = defaultRepName==name;
        jQ("#rep_temp").parent().append(rep);
        rep.find("span.repName").text(name);
        if(isDefault){
            rep.find("span.repName").addClass("defaultRep");
        }
        rep.find("input.repName").val(name).change(function(){
            var e = jQ(this);
            var oldName = name;
            name = e.val().replace(/\s+/g, "");
            e.val(name);
            if(name=="" || repsData[name]){
                name = oldName;
                e.val(name);
                return;
            }
            data.name = name;
            rep.attr("id", "rep_" + name);
            rep.find("span.repName").text(data.name);
            if(configData.settings.defaultRepositoryName.value==oldName){
                configData.settings.defaultRepositoryName.value=name;
            }
            repsData[name] = data;
            delete repsData[oldName];
        });
        //Note: IE change event does not fire on radio buttons
        rep.find("input.repDefault").attr("checked", isDefault).click(function(){
            var e = jQ(this);
            e.attr("checked", true);
            rep.siblings().find("input.repDefault").attr("checked", false)
            rep.siblings().find("span.repName").removeClass("defaultRep");
            configData.settings.defaultRepositoryName.value = name;
            rep.find("span.repName").addClass("defaultRep");
        });
        rep.find("input.repUrl").val(data.url).change(function(){
            var e = jQ(this);
            data.url = e.val();
        });
        rep.find("input.repPath").val(data.path).change(function(){
            var e = jQ(this);
            data.path = e.val();
        });
        rep.find("input.repTempPath").val(data.documentTemplatesPath).change(function(){
            var e = jQ(this);
            data.documentTemplatesPath = e.val();
        });
        rep.find("input.repExportPath").val(data.exportPath).change(function(){
            var e = jQ(this);
            data.exportPath = e.val();
        });
        rep.find("button.deleteButton").click(function(){
            // are you sure?
            delete repsData[name];
            rep.remove();
        });
        rep.find("td.repSettings").append(settingsNode);
        loadSettingsData(settingsNode, data.settings);
    }


    jQ("div.helptext").each(function(){
        var d=jQ(this);
        var title=d.attr("title");
        var q=jQ("<span class='help' title='What&apos;s this?'>?</span>");
        d.after(q);
        q.click(function(){
            dialog.dialog("close");
            dialog.html(d.html());
            dialog.dialog({
                "width":"480px", "height":"320px",
                "modal":false, "resizable":true, "draggable":true,
                "title":title,
                "buttons": {"OK": function(){dialog.dialog("close");} }
            });
        });
    });


    jQ("button.saveButton").click(function(){
        var id = jQ(this).attr("id")
        function callback(data){
            var tempMsg = jQ("#tempMessage");
            if(data.error){
                tempMsg.css("color", "red");
                tempMsg.text(data.error).show().hide(2000);
            } else {
                tempMsg.css("color", "green");
                tempMsg.html("Saved OK").show().hide(2000);
                if(id=="saveAndClose"){
                    function callback2(data){
                        var href = window.location.href;
                        try{
                            if(href.slice(-11)==="edit-config") href = href.slice(0,-11);
                        }catch(e){}
                        window.location.href = href;
                    }
                    ajax("restart", {}, callback2);
                    tempMsg.html("Reloading. Please wait..").show().hide(20000);
                }else{
                    loadData(data);
                }
            }
        }
        ajax("save", {"data":JSON.stringify(configData)}, callback);
    });

    jQ("#closeButton").click(function(){
        var href = window.location.href;
        try{
            if(href.slice(-11)==="edit-config") href = href.slice(0,-11);
        }catch(e){}
        window.location.href = href;
    });


    jQ("#testButton").click(function(){
        function callback(data){
            //alert("Saved OK");
            var tempMsg = jQ("#tempMessage");
            tempMsg.css("color", "red");
            tempMsg.text(data.error || data.ok).show().hide(2000);
        }
        //ajax("test", {}, callback);
        ajax("restart", {}, callback);
    });


    jQ("#clearAddNewRep").click(function(){
        jQ("div.addNewRep input").val("");
    });

    jQ("#submitAddNewRep").click(function(){
        // Add a new repository
        var name, url, path, reps;
        name = jQ("#newRepName").val();
        url = jQ("#newRepUrl").val();
        path = jQ("#newRepPath").val();
        reps = configData.repositories;
        if(name==""){
            try{
                var from = path || url;
                if(from!=""){
                    parts = from.replace(/\\/g, "/").split("/").reverse();
                    name = parts[0];
                    if(name=="") name = parts[1];
                }
                var count = "";
                if(name!=""){
                    while(reps[name + count]){
                        if(count=="") count=1;
                        count += 1;
                    }
                    name += count;
                }
            }catch(e){

            }
        }
        if(name!=""){
            if(reps[name]){
                alert("'"+name+"' already in use!");
            }else{
                var settings = configData.settings;
                var defaultExportPath = (settings.defaultExportPath || {}).value || "";
                var defaultDocumentTemplatesPath = (settings.defaultDocumentTemplatesPath || {}).value || "";
                reps[name] = {name:name, url:url, path:path, settings:{},
                            exportPath:defaultExportPath,
                            documentTemplatesPath:defaultDocumentTemplatesPath};
                addRep(name, reps);
                jQ("#addrep").parent().append(jQ("#addrep"));
                jQ("div.addNewRep input").val("");
                jQ(".accordion:last").accordion("activate", false);
            }
        }
    });
    try {
        jQ(".accordion").accordion({"header":"h6", "alwaysOpen":false, "autoHeight":false, "active":false});
    } catch(e) {
        alert(e.message);
    }

    jQ("#resetButton").click(function(){
        loadData(configDataBackup);
    });

    ajax("getCommonSettings", {}, function(data){
        commonSettings = data;
    });
    setTimeout(function() {
            ajax("getData", {}, loadData);
        }, 100)
}

jQuery(function(){  // on loaded
    editConfig(jQuery);
});
