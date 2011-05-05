// =======================================
// Glossary Hover
// =======================================

var jQ = jQuery;
jQ(function() {
	 jQ("span.glossary-term").mouseover(function(e){
	 
 			thisTop = jQ(this).position().top;
	 		thisLeft = jQ(this).position().left ;
	 		width = jQ(this).width();
	 		id = jQ(this).text(); 
			if (id.indexOf("*") != -1){
				id= id.substr(0,id.indexOf("*")); 
			}
			id = "#"+id;
			jQ(id).removeClass("glossary-def"); 
	 		jQ(id).addClass("glossary-def-hover"); 
	 		
			t =  thisTop - jQ(id).position().top + 10; 
	 		l =thisLeft - jQ(id).position().left + 5;
	 		
	 		jQ(id).css({ top:t, left: l });
	 		//right margin
	 		if (jQ(id).position().left > jQ("div.body").width()){
	 			l = l - jQ(id).width();
	 			jQ(id).css({ top:t, left: l });
	 		}
	 		
	 });
	 jQ("span.glossary-term").mouseout(function(e){ 
	 		id = jQ(this).text(); 
			if (id.indexOf("*") != -1){
				id= id.substr(0,id.indexOf("*")); 
			}
			id = "#"+id;
			jQ(id).removeClass("glossary-def-hover"); 
	 		jQ(id).addClass("glossary-def"); 
	 		jQ(id).css({ top:0, left: 0 });  
	 		
	 });
 });