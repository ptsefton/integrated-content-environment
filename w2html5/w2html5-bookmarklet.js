/*
 * jQuery Bookmarklet - version 1.0
 * Originally written by: Brett Barros
 * With modifications by: Paul Irish
 *
 * If you use this script, please link back to the source
 *
 * Copyright (c) 2010 Latent Motion (http://latentmotion.com/how-to-create-a-jquery-bookmarklet/)
 * Released under the Creative Commons Attribution 3.0 Unported License,
 * as defined here: http://creativecommons.org/licenses/by/3.0/
 *
 *  <a href="javascript:(function(){var head=document.getElementsByTagName('head')[0],script=document.createElement('script');script.type='text/javascript';script.src='http://integrated-content-environment.googlecode.com/svn/branches/temp-2011/w2html5/w2html5-bookmarklet.js?' + Math.floor(Math.random()*99999);head.appendChild(script);})(); void 0">Word2HTML5</a>
 *
 */
 
window.bookmarklet = function(opts){fullFunc(opts)};
 
// These are the styles, scripts and callbacks we include in our bookmarklet:
window.bookmarklet({
 
    css : ['http://integrated-content-environment.googlecode.com/svn/branches/temp-2011/w2html5/w2html5ext/w2html5.css'],
    js  : ['http://integrated-content-environment.googlecode.com/svn/branches/temp-2011/w2html5/w2html5ext/w2html5.js'],    
    jqpath : 'http://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js', 
    ready : function(){
 
		//TODO - call the conversion code instead of having it run on load
 
   	    }
})
 
function fullFunc(a){function d(b){if(b.length===0){a.ready();return false}$.getScript(b[0],function(){d(b.slice(1))})}function e(b){$.each(b,function(c,f){$("<link>").attr({href:f,rel:"stylesheet"}).appendTo("head")})}a.jqpath=a.jqpath||"http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js";(function(b){var c=document.createElement("script");c.type="text/javascript";c.src=b;c.onload=function(){e(a.css);d(a.js)};document.body.appendChild(c)})(a.jqpath)};
