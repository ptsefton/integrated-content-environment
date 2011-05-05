/*
 * Copyright (C) 2010 University of Southern Queensland
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 * 
 */
var jQ=jQuery;

/*
jQ(function(){
    var paquete = paqueteFactory(jQ);
    paquete.getManifestJson();
});
*/
var paqueteFactory = function(jQ){
    var paquete = {};
    var pages = {};     // cache
    var homePage;
    var nodes;
    
    paquete.contentBaseUrl = "";
    paquete.contentSelector = "#content";
    paquete.titleSelector = "#contents-title";
    paquete.tocSelector = "#toc .toc";
    paquete.contentScrollToTop = function(){jQ(window).scrollTop(0);};
    paquete.contentLoadedCallback = null;
    paquete.updateTOC = updateTOC;
    
    
    //navigation form 
    paquete.useNavigation = false;
    paquete.navFormSettings = {};
    paquete.onNavFormDisplay = null;
    paquete.includeTopButton = true;
    paquete.getThisNodeHash = getThisNodeHash;
    paquete.getCurrentDoc = getCurrentDoc;
    
    
    paquete.updateContent = function(content) {
        var contentDiv=jQ(paquete.contentSelector);
        contentDiv.children().hide();
        contentDiv.append(content);
        if(content.is(":visible")){
            try{
                contentDiv.find("#loadingMessage").remove();
                if(paquete.contentLoadedCallback) paquete.contentLoadedCallback(paquete);
            }catch(e){
                alert("Error calling loadedContentCallback: " + e)
            }
        }else{
            try{
                content.show();
            }catch(e){ alert("Error in loading content: "+e); }
        }
         
        if(paquete.updateTOC)    paquete.updateTOC();
        // Refesh hash so that the browser will go any anchor locations.
        if(window.location.hash) setTimeout(function(){window.location.hash=getLocationHash();}, 500);
    };
    paquete.setTitle = function(title) {
        jQ(paquete.titleSelector).html(title);
    };
    
    paquete.getManifestJson = function(jsonFilename) {
        if(!jsonFilename) jsonFilename="manifest.json";
        jQ.get(jsonFilename, {}, processManifestJson, "json");       // "imsmanifest.json"
    };
    paquete.displayTOC = function(nodes) {
        function getList(data){
            var items = [];
            var list = "";
            //data.forEach(function(i){ //not working for IE
            jQ.each(data,function(c,i){
                // title, relPath, visible
                if(i.visible!==false) {
                    var href = (i.relPath || i.attributes.id);
                    var title = i.title || i.data;
                    var children = "";
                    if(i.children) children=getList(i.children);
                    if(href.substring(href.length-4)===".htm") href="#"+href;
                    items.push("<li><a href='"+href+"'>"+title+"</a>"+children+"</li>");
                }
            });
            if(items.length) { list = "<ul>\n" + items.join("\n") + "</ul>\n"; }
            return list;
        }
        if(paquete.useNavigation) createNavigation();
        jQ(paquete.tocSelector).html(getList(nodes));
        function onLocationChange(location, data){
            hash = data.hash;
            hash = hash.split("#")[0];
            jQ("a").removeClass("link-selected");
            jQ("a[href='#"+hash+"']").addClass("link-selected");
        }
        jQ(window.location).change(onLocationChange);
    };
    paquete.loadingMessage = "Loading. Please wait...";

    function processManifestJson(data) {
        if(!data) return;
        if(data.title) paquete.setTitle(data.title);
        // Note: homePage & nodes are package level variables
        homePage = data.homePage;
        ns = data.toc || data.nodes;
        nodes = [];
        jQ.each(ns, function(c, i){
            var visible=(i.visible!==false);
            if(visible) nodes.push(i);
        });
        function multiFormat(c, i){
            var visible=(i.visible!==false);
            var id=(i.relPath || i.attributes.id);
            var title=(i.title || i.data);
            i.visible=visible;
            i.relPath=id;
            if(!i.attributes) i.attributes={};
            i.attributes.id=id;
            i.title=title; i.data=title;
            jQ.each(i.children, multiFormat);
        }
        jQ.each(nodes, multiFormat);
        if(!homePage || homePage=="toc.htm") {
            if(nodes.length>0){
                homePage=nodes[0].relPath;
                if(!window.location.hash)  window.location.hash = homePage;
            }else{
                homePage=""; 
                paquete.updateContent("[No content]");
            }
        }
        paquete.displayTOC(nodes);
        
        checkForLocationChange();
        setInterval(checkForLocationChange, 10);
    }
    function getRawLocationHref(){
        //get full URL.
        return window.location.href;
    }
    
    function getLocationUrl(){
        //get the actual URL without hash. or parameter. 
        var href;
        href = window.location.href;
        href = href.split("#",1)[0];
        //href = href.split("?", 1)[0];
        return href;
    }
    function getLocationHash(){
        //get hash location.
        var hash;
        hash = window.location.hash;
        hash = fixHashLocation(hash);
        return hash;
    }
    function fixHashLocation(hash){
        if(!hash || ! hash.length){ 
            return ;
        }
        if(hash.substring(0,1) ==="#") hash=hash.substring(1); //remove first #
        hash = hash.replace(/%23/g, "#");
        return hash;
    }
    function checkForLocationChange() {
        href = getRawLocationHref();
        if(checkForLocationChange.href!== href){
            var hashOnly=false; hash = getLocationHash();
            //if(hash.length) hash=hash.substring(1);
            if(checkForLocationChange.href){
                hashOnly=(checkForLocationChange.href.split("#",1)[0])===(href.split("#",1)[0]);
            }
            checkForLocationChange.href = href;
            jQ(window.location).trigger("change", {hash:hash, hashOnly:hashOnly});
        }
    }
    function createNavigation(){
        //now move the navigation
        if(paquete.useNavigation){
            if(paquete.onNavFormDisplay){
                navForm = navigationFormFactory(paquete.navFormSettings,paquete.includeTopButton);
                paquete.onNavFormDisplay(navForm);
                return;
            }
            topNavForm = navigationFormFactory(paquete.navFormSettings,false);
            jQ(paquete.contentSelector).before(topNavForm);
            bottomNavForm = navigationFormFactory(paquete.navFormSettings,true);
            jQ(paquete.contentSelector).after(bottomNavForm);
        }
    }
    function checkNavigation(selectedNode){
        
        prevSelector = getClassSelector(paquete.navFormSettings.prevStyle);
        jQ(prevSelector).unbind("click"); //just to make sure it does not bind with 2 function
        jQ(prevSelector).bind("click", paquete.navFormSettings.prevFunction)
        jQ(prevSelector).html(paquete.navFormSettings.prevLabel);
        prevNode = findPrev(selectedNode);
        if(!prevNode || prevNode.size() === 0){
            //first document so disable the prev button
            jQ(prevSelector).unbind("click"); 
            jQ(prevSelector).html(paquete.navFormSettings.inactivePrevLabel);
            //jQ(prevSelector).hide();
        }
        
        nextSelector = getClassSelector(paquete.navFormSettings.nextStyle);
        jQ(nextSelector).unbind("click"); //just to make sure it does not bind with 2 function
        jQ(nextSelector).bind("click", paquete.navFormSettings.nextFunction)
        jQ(nextSelector).html(paquete.navFormSettings.nextLabel);
        nextNode = findNext(selectedNode);
        if(!nextNode || nextNode.size() === 0){
            //last document so disable the next button
            jQ(nextSelector).unbind("click"); 
            jQ(nextSelector).html(paquete.navFormSettings.inactiveNextLabel);
        }
        //not working well yet..
        topSelector = getClassSelector(paquete.navFormSettings.topStyle);
        jQ(topSelector).unbind("click"); //just to make sure it does not bind with 2 function
        jQ(topSelector).bind("click", paquete.navFormSettings.topFunction)
        jQ(topSelector).html(paquete.navFormSettings.topLabel);
        //check if there is a scroll bar
        if(jQ(window).height()>=jQ(paquete.contentSelector).innerHeight()){ //not very good idea. 
            //last document so disable the next button
            jQ(topSelector).unbind("click"); 
            jQ(topSelector).html(paquete.navFormSettings.inactiveTopLabel);
        }
    }
    function getClassSelector(name){
            return "."+name;
    }
    function setHash(hash){
        //fix for IE whose href is whole url
        hash = hash.split("#")[1];
        hash = fixHashLocation(hash)
        window.location.hash = hash;
    }
    function getCurrentDoc(){
        return jQ(paquete.tocSelector).find("li.selected");
    }
    function getThisNodeHash(node){
        return node.find("a").attr('href');
    }
    function findPrev(currentNode){
        prevNode = currentNode.prev("li");
        if(prevNode.size() === 0){
            //if cannot find prev li node. This must be the first child of the current list ,so check if it has parent. 
            parentNode = currentNode.parents("li");
            if(parentNode.size()!== 0) return parentNode; 
            return ;
        }
        if(prevNode.children("ul").children("li").size()!== 0){
           return prevNode.children("ul").children("li:last");
        }
        return prevNode;
    }
    function findNext(currentNode){
        //check if there is any children
        if(currentNode.children("ul").children("li").size() !== 0) {
            return currentNode.children("ul").children("li:first");
        }
        nextNode = currentNode.next("li");
        if(nextNode.size() === 0){
            //check if there is a parent, if there is then use parent next sibling
            parentNode = currentNode.parents("li");
            if(parentNode.size() === 0 ) {return; }//if no parent, end of list.
            nextNode = parentNode.next("li");
            if(nextNode.size() === 0){ console.log("end of list");return; }//if no parent next sibling, end of list
        }
        return nextNode;
    }
    function goPrev(){
        currentNode = paquete.getCurrentDoc();
        prevNode = findPrev(currentNode);
        setHash(paquete.getThisNodeHash(prevNode));
    }
    function goNext(){
        currentNode = paquete.getCurrentDoc();
        nextNode =findNext(currentNode);
        setHash(paquete.getThisNodeHash(nextNode));
    }
    function goTop(){
        paquete.contentScrollToTop();
    }
    var navigationFormFactory = function(settings,includeTop){
        //creating the form
        var navForm = {};
        var prevButton, topButton,nextButton;
        //just to make sure we have everything. 
        settings.style = settings.style || "paquete-navigation";
        settings.prevStyle = settings.prevStyle || "nav-prev";
        settings.nextStyle = settings.nextStyle || "nav-next";
        settings.topStyle =  settings.topStyle || "nav-top";
        settings.prevLabel =settings.prevLabel ||"[<]";
        settings.nextLabel =settings.nextLabel ||"[>]";
        settings.topLabel =settings.topLabel ||"[Top]";
        settings.prevFunction =settings.prevFunction ||goPrev;
        settings.nextFunction =settings.nextFunction ||goNext;
        settings.topFunction =settings.topFunction ||goTop;
        settings.inactivePrevLabel =settings.inactivePrevLabel ||settings.prevLabel;
        settings.inactiveNextLabel =settings.inactiveNextLabel ||settings.nextLabel;
        settings.inactiveTopLabel =settings.inactiveTopLabel ||settings.topLabel;
        
        navForm = jQ("<div class=\""+settings.style+"\"></div>");
        
        prevButton = jQ("<span class='"+settings.prevStyle+"'>"+settings.prevLabel+"</span>");
        prevButton.click(settings.prevFunction);
        navForm.append(prevButton);
        if(includeTop && paquete.includeTopButton){
             topButton = jQ("<span class='"+settings.topStyle+"'>"+settings.topLabel+"</span>");
             topButton.click(settings.topFunction);
             navForm.append(topButton);
        }
        nextButton = jQ("<span class='"+settings.nextStyle+"'>"+settings.nextLabel+"</span>");
        nextButton.click(settings.nextFunction );
        navForm.append(nextButton);
        return navForm;
    }
    function updateTOC(){
        //fix CSS to select current selection
        var hash,href;
        hash = getLocationHash();
        hash = hash.split("#")[0];
        selectedNode = jQ(paquete.tocSelector).find("a[href='"+"#"+hash+"']").parent("li");
        if(selectedNode.size() === 0){
            //fix for IE. IE replace the hash value with href+hash
            href = getLocationUrl();
            selectedNode = jQ(paquete.tocSelector).find("li:has(a[href='"+href+"#"+hash+"'])");
            if(selectedNode.size() === 0) alert("Error in Updating TOC: Cannot find current document to highlight");
        }
        jQ(paquete.tocSelector).find("li").removeClass("selected");
        jQ(paquete.tocSelector).find("li>ul").addClass("hide");
        selectedNode.closest("ul").removeClass("hide");
        selectedNode.addClass("selected");
        if(paquete.useNavigation){
            //if change check if it is the first one or last one. 
            checkNavigation(selectedNode);
        }
    }
    
    
    function onLocationChange(location, data){
        hash = data.hash;
        hash = fixHashLocation(hash);
        hash = hash.split("#")[0];
        if(data.hashOnly){
            if(hash===onLocationChange.hash) return;
        }
        
        onLocationChange.hash = hash;
        if(hash==="") hash=homePage;
        if(pages[hash]) {
            paquete.contentScrollToTop();
            paquete.updateContent(pages[hash]);
            return;
        }
        function getHPath(p) {
            // returns hPath or nUll (make a relative path an absolute hash path)
            var ourParts, ourDepth, upCount=0, depth, hPath;
            if(p.slice(0,1)==="/" || p.search("://")>0) return null;
            ourParts = hash.split("/");
            ourDepth = ourParts.length-1;
            p = p.replace(/[^\/\.]+\/\.\.\//g, "");
            p = p.replace(/\.\.\//g, function(m){upCount+=1; return "";});
            depth = ourDepth-upCount;
            if(depth<0) return null;
            hPath = ourParts.slice(0,depth).concat(p.split("/")).join("/");
            return hPath
        }
        function callback(data) {   // ICE content data
            var h, anchors={};
            var pageToc = jQ(data).find("div.page-toc");
            var body = jQ(data).find("div.body");
            body.find("div.title").show().after(pageToc);
            body.find("a").each(function(c, a) { 
                var ourUrl = getRawLocationHref().split("#",1)[0];
                a=jQ(a); h = a.attr("href");
                if(h){
                    if(h.substring(0, ourUrl.length)===ourUrl){
                        h = h.substring(ourUrl.length);
                    }
                    if(h.substring(0,1)==="#"){
                        a.attr("href", "#"+hash+h);
                        anchors[h.substring(1)]=hash+h;
                    }else{
                        if(h=getHPath(h)){
                            a.attr("href", "#"+h);
                        }
                    }
                }
            });
            body.find("a").each(function(c, a) { 
                var id, name;
                a=jQ(a); 
                id=a.attr("id"); name=a.attr("name");
                if(anchors[id]){
                    a.attr("name", anchors[id]);
                    a.prepend("<span id='"+anchors[id]+"' />");
                }else if(anchors[name]){
                    a.attr("name", anchors[name]);
                }
            });

            var a = getLocationHash();
            if(a.substring(0,1)=== "#") a = a.substring(1); //remove # if first one is that. 
            var loc = getLocationUrl();
            loc = loc.split("?",1)[0];
            var tmp = loc.split("/"); 
            tmp.pop(); 
            loc=tmp.join("/");
            
            var baseUri = paquete.contentBaseUrl.toString();
            if(baseUri.search(/\/$/)===-1) baseUri +="/";
            baseUri += a.split("/").slice(0,-1).join("/");
            if(baseUri[baseUri.length-1]!=="/") baseUri +="/";
            function updateUri(node,attrName){
                var a = node.attr(attrName);
                function testIfLocalUri(uri){
                    if (!uri){return false;}
                    return uri.search(/^\/|\:\/\//g)===-1;
                }
                if(a.substring(0, loc.length)===loc){
                   //IE7 image Fixup. 
                   a = a.substring(loc.length+1);
                }
                if(testIfLocalUri(a)){
                    node.attr(attrName,baseUri+a);
                }
            }
            body.find("*[src]").each(function(c,node){
                node = jQ(node);
                updateUri(node,"src");
            });
            body.find("object").each(function(c,node){
                node = jQ(node);
                updateUri(node,"data");
                updateUri(node,"codebase");
                node.find("param[name='movie'],param[name='url'],param[name='media']").each(function(c,node){
                    node = jQ(node);
                    updateUri(node,"value");
                });
            });
            
            var html = body.find(">div");
            pages[hash]=html;
            paquete.updateContent(pages[hash]);
        }
        paquete.updateContent(jQ("<div style='display:none;' id='loadingMessage'>"+paquete.loadingMessage+"<div>"));
        jQ.get(paquete.contentBaseUrl+hash, {}, callback, "html");
    }

    jQ(window.location).change(onLocationChange);
    
    paquete.processManifestJson = processManifestJson;
    return paquete;
};