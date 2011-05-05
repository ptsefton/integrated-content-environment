/*

External Link v1.0.6
(c) Arc90, Inc.

http://www.arc90.com
http://lab.arc90.com

Licensed under : Creative Commons Attribution 2.5 http://creativecommons.org/licenses/by/2.5/
Modified: USQ 2007-11-01
*/

/* Globals */
var arc90_isIE = document.all? true: false;
var arc90_extLinkUseClassName = false;

function arc90_extlink() {
	var b = document.domain;
	if(b=="") b="file://"
	var A = document.getElementsByTagName('A');
	for (var i = 0, l = A.length; i < l; i++) {
		var a = A[i];
		if (((b != '' && a.href.indexOf(b) < 0) || b == '') && a.href.indexOf('://') > 0 && ((arc90_extLinkUseClassName && a.className.indexOf('extlink') >= 0) || !arc90_extLinkUseClassName)) {
            try {
				var m = arc90_newNode('span', '', 'extlinkIMG');
				m.border = 0;
				m.title = '[External Link]';
				if (arc90_isIE) { m.style.zoom = '100%';  m.style.padding = '0'; }
				eval('arc90_addEvent(m, "click", function() { window.open("'+ a.href +'"); });');
				a.parentNode.insertBefore(m, a.nextSibling);
				if (a.target=='')
					a.target='_blank'
			} catch(err) { a = null;}
		}
		if ((a.onclick && a.href.indexOf(b) > 0) || (a.onclick && a.href.indexOf(':///') > 0) || (a.target=='_blank' && a.href.indexOf(b) > 0) || (a.target=='_blank' && a.href.indexOf(':///') > 0))  {
		 try {
				var m = arc90_newNode('span', '', 'blanklinkIMG');
				m.border = 0;
				m.title = '[New Window]';
				if (arc90_isIE) { m.style.zoom = '100%';  m.style.padding = '0'; }
				eval('arc90_addEvent(m, "click", function() { window.open("'+ a.href +'"); });');
				a.parentNode.insertBefore(m, a.nextSibling);
				/* a.target = '';*/
			} catch(err) { a = null;} 
		}  
	}
}

/* Events */
function arc90_isString(o) { return (typeof(o) == "string"); }

function arc90_addEvent(e, meth, func, cap) {
	if (arc90_isString(e))	e = document.getElementById(e);

	if (e.addEventListener){
		e.addEventListener(meth, func, cap);
    		return true;
	}	
	else if (e.attachEvent){
			return e.attachEvent("on"+ meth, func);
		}
	return false;
}

/* Nodes */
function arc90_newNode(t, i, s, x, c) {
	var node = document.createElement(t);
	if (x != null && x != '') {
		var n = document.createTextNode(x);
		node.appendChild(n);
	}
	if (i != null && i != '')
		node.id = i;
	if (s != null && s != '')
		node.className = s;
	if (c != null && c != '')
		node.appendChild(c);
	return node;
}

/* Onload */
arc90_addEvent(window, 'load', arc90_extlink);

