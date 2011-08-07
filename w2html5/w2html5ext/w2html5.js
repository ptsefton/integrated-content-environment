/*

COPYRIGHT Peter Malcolm Sefton 2011

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.



*/

//TODO - capture everything after "-" in a style name and use a class on generated p or h

//TODO Add a config object

//TODO - add regular expressions to boil down styles
headingStyles = {
"h1n" : "h2",
"h1" : "h2",
"h2n" : "h3",
"h2n" : "h3",
"h3n" : "h4",
"h3n" : "h4",
"msotitle" : "h1",
"title" : "h1"
};

function stateFactory(jQ, topContainer) {
	var state = {};
	state.indentStack = [0];
 	state.elementStack = [topContainer];
	state.currentIndent = 0;
	function setCurrentIndent(indent) {
		state.currentIndent = indent;
	}
	state.setCurrentIndent = setCurrentIndent;
	function nestingNeeded() {
		//Test whether current left=margin indent means we should add some nesting
		return(state.currentIndent > state.indentStack[state.indentStack.length-1]);
		
	}
	state.nestingNeeded = nestingNeeded;
	function levelDown() {
		while (state.currentIndent < state.indentStack[state.indentStack.length-1]) {
			popState();
		}
			
	}
	state.levelDown = levelDown;
	function getCurrentElement() {
		return state.elementStack[state.elementStack.length-1];
	}
	state.getCurrentElement = getCurrentElement;
	function popState() {
		state.indentStack.pop();
		state.elementStack.pop();
	}
	state.popState = popState;
	function pushState(el) {
		state.indentStack.push(state.currentIndent);
		state.elementStack.push(el);
	}
	state.pushState = pushState;
	function resetState() {
		state.indentStack = [0];
		state.elementStack = [state.elementStack[0]];
	}
	state.resetState = resetState;
	return state;
}

function loseWordMongrelMarkup(doc) {


	 

		//Deal with MMDs        
		startComment = /<\!--\[(.*?)\]\>/g;
		startCommentReplace = "<span title='start-$1'/><xml class='mso-conditional'>";
		doc = doc.replace(startComment, startCommentReplace);
		
		endComment = /<\!\[(.*?)\]--\>/g;
		endCommentReplace = "</xml><span title='end-$1'/>";
		doc = doc.replace(endComment, endCommentReplace);

		//Ordinary condition comment
		comment = /<\!--\[(.*?)\]--\>/g;
		commentReplace = "";
		doc = doc.replace(startComment, commentReplace);
	      
		startMMD = /<\!\[(.*?)\]\>/g;
		startMMDReplace = "<span title='$1'/>";
		doc = doc.replace(startMMD, startMMDReplace);


		
		endMMD = /<\!\[endif\]>/g;
		endMMDReplace = "<span title='endif'/>";
		doc = doc.replace(endMMD, endMMDReplace);

		//This is a rare special case, seems to be related to equations
		wrapblock = /<o:wrapblock>/g;
		wrapblockreplace = "<span title='wrapblock' ><!-- --></span>";
		doc = doc.replace(wrapblock, wrapblockreplace);

		endwrapblock = /<\/o:wrapblock>/g;
		endwrapblockreplace = "<span title='end-wrapblock' ><!-- --></span>";
		doc = doc.replace(endwrapblock, endwrapblockreplace);

	    
		return doc;	

}

function getRidOfExplicitNumbering(element) {
	//Get rid of Word's redundant numbering (Note, don't don't do this on headings)
	$(element).find("span[style='mso-list:Ignore']").remove();
	
}
function getRidOfStyleAndClass(element) {
	$(element).attr("style", "");
	$(element).attr("class", "");
}


function rewrite() {
  //TODO - recurse into tables

  //Container for our page
  art = $("<article></article>")	 
  
  //Make the assumption Normal has zero indent
  //TODO work out zero indent from Normal style (and deal with negative indents?)
  state = stateFactory(art);
  $("body > *").each (
    
    function (index) {
	if (index == 0)  {
		$("body").prepend($(art));
	}
	classs = String($(this).attr("class")).toLowerCase();
	// Normalise some styles
	
	tag = headingStyles[classs];
	if (tag) { //Found a heading - close all containers
 		 state.resetState();
	} else {
		state.setCurrentIndent(parseFloat($(this).css("margin-left")));
	}


	var type = "p";
	
      	//USe ICE style conventions to identify lists 
	if (classs.substr(0,2) == "li") {
		type = "li";
		listType = classs.substr(3,1);	
		if (listType == "n") {
			listType = "1";
		}	
	} 
	
 	if (type == "p") {
		style = $(this).attr("style");
		//TODO This will fail on adjacent lists (or other things) with same depth but diff formatting
		if ( style && (style.search(/mso-list/) > -1)) {
			
			type = "li";
			//If this is a new list try to work out its type
			if (state.nestingNeeded()) {
				number = $(this).find("span[style='mso-list:Ignore']").text();
				if (number.search(/A/) > -1) {
					listType = "A";
				}
				else if (number.search(/a/) > -1) {
					listType = "a";
				}
				else if (number.search(/I/) > -1) {
					listType = "I";
				}
				else if (number.search(/i/) > -1) {
					listType = "i";
				}
				else {
					listType = "b"; //Default to bullet lists
				}
			}
			
		}
		else if (span = $(this).find("span:only-child")) {
			//We have some paragraph formatting
			fontFamily = span.css("font-family");
			//Word is not supplying the generic-family for stuff in Courier so sniff it out
			//TODO: add other monospaced fonts and put this in config
			preMatch = /(courier)|(monospace)/i
			
			if (fontFamily && (fontFamily.search(preMatch) > -1)) {
				type = "pre";
			}
			
		}

	}
	//Get rid of formatting now
	getRidOfStyleAndClass($(this));

        

	state.levelDown(); //If we're embedded to far, fix that
	
        if (state.nestingNeeded()) {
		
		//Put this inside the previous container element - we're going deeper
		$(this).appendTo(state.getCurrentElement());
		if (type == "li") {
                        if (listType == "b") {
				$(this).wrap("<ul><li></li></ul>");
			}

			else {
			 	$(this).wrap("<ol type='" + listType + "'><li></li></ol>");
			}
			//TODO look at the number style and work out if we need to restart list numbering
			//The style info has a pointer to a list structure - if we see a new one restart the list

			
			getRidOfExplicitNumbering($(this));
			
			
		}
		else if (type == "pre") {
			$(this).wrap("<pre></pre>");
			//TODO: fix unwanted line breaks
			$(this).replaceWith($(this).text().replace(/\r/," "));
		}	
		else {
			 $(this).wrap("<blockquote></blockquote>");
			 
		}
		//All subsequent paras at the right level and type should go into this container
                //So remember it
		//TODO - wrap this in a proper state object rather than the parallel arrays: FRAGILE!
		state.pushState($(this).parent());
		
		
		
	}
	else {
		
		
		if (type == "li") {
			$(this).appendTo(state.getCurrentElement().parent());
			$(this).wrap("<li></li>");
			getRidOfExplicitNumbering($(this));
			
		}
		else {

			$(this).appendTo(state.getCurrentElement())		;
			if (tag) {
				//It's a heading
				$(this).replaceWith("<" + tag + ">" + $(this).html() + "</" + tag + ">");

			} 
			else if (type == "pre") {
				//TODO: Get rid of this repetition (but note you have to add $(this) to container b4 wrapping or it won't work)
				$(this).wrap("<pre></pre>");
				$(this).replaceWith($(this).text());
			}
		}	
			
		}
		
	}
      
 
  )
}

//Start by string-processing MSO markup into something we can read and reloading
$("head").html(loseWordMongrelMarkup($("head").html()));

$("body").html(loseWordMongrelMarkup($("body").html()));

// TODO alert(loseWordMongrelMarkup("<![if !supportLists]>"));

//Get rid of the worst of the emndded stuff
$("xml").remove();
//Get rid of Word's sections
$("div").each(
function(index) {
   $(this).children(":first-child").unwrap();
}
)


rewrite();

//Clean it all up
$("p:empty").remove();
$("span:empty").remove();
$("span[mso-spacerun='yes']").remove(); //.replacewith(" ");

$("xml").remove();
$("v:shapetype").remove();

//TODO: get rid of reams of other crap from Word






