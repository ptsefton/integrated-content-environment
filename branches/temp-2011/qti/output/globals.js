function OpenNewWindow(URL, wName, sizeOfWin) {
  var xtraWindow;
  var wSettings = 'status=yes,scrollbars=yes,resizable=yes';
  var maxW = screen.width;
  var maxH = screen.height;
  var scaleH, scaleV;
  var wTop = 15;
  var wLeft = 20;
  var wW, wH;

  if (wName == null | wName == '') { wName = 'newwin'; }
  if (maxW == 0 | maxW == '') {maxW = 640;}
  if (maxH == 0 | maxH == '') {maxH = 480;}

  if (sizeOfWin == 'tiny') {
     wSettings += ',toolbar=no,menubar=no,location=no';
     scaleW = 0.90; scaleH = 0.20;}
  else if (sizeOfWin == 'small') {
     wSettings += ',toolbar=no,menubar=no,location=no';
     scaleW = 0.90; scaleH = 0.40;}
  else if (sizeOfWin == 'medium') {
     wSettings += ',toolbar=no,menubar=yes,location=no';
     scaleW = 0.90; scaleH = 0.60;}
  else if (sizeOfWin == 'video') {
     wSettings += ',toolbar=no,menubar=no,location=no';
     scaleW = 0.60; scaleH = 0.60;}
  else {
     wSettings += ',toolbar=yes,menubar=yes,location=yes';
     scaleW = 0.90; scaleH = 0.75;}

  wH = maxH * scaleH;
  wW = maxW * scaleW;

  wSettings += ',top=' + wTop + ',left=' + wLeft;
  wSettings += ',width=' + wW + ',height=' + wH;

  xtraWindow=window.open(URL, wName, wSettings);
  try { xtraWindow.focus(); } catch(err) {}
}

/* functions for hybrid inline cma */

function hideElement(id) {
  var elem = document.getElementById(id);
  if (elem != null) {
    elem.style.display = "none";
  }
}

function showElement(id) {
  var elem = document.getElementById(id);
  if (elem != null) {
    elem.style.display = "block";
  }
}

function showHowJudged(id, correct) {
  var elem = document.getElementById(id);
  if (elem != null) {
    if (correct == true) {
      elem.className = "feedback-correct";
    } else {
      elem.className = "feedback-incorrect";
    }
  }
}

function cmaOption(item, option, count) {
  for (var i = 1; i <= count; i++) {
    if (i == option) {
      showElement(item + '_' + i + '_s');
    } else {
      hideElement(item + '_' + i + '_s');
    }
  }
  if (option == count) {
  showHowJudged(item + '_fb', true);
  } else {
  showHowJudged(item + '_fb', false);
  }
  showElement(item + '_fb');
}

function cmaClear(item, count) {
  /*
  for ( var i = 1; i<= count; i++) {
    document.getElementById(item + '_' + i).checked = false;
    hideElement(item + '_' + i + '_s');
  }
  hideElement(item + '_i');
  hideElement(item + '_c');
  hideElement(item + '_gen');
  */
  hideElement(item + '_fb');
}

function cmaJudge(item, count, answer) {
  var theanswer = '';
  for ( var i = 1; i<= count; i++) {
    if (document.getElementById(item + '_' + i).checked == true) {
      theanswer += '1';
      showElement(item + '_' + i + '_s');
    } else {
      theanswer += '0';
      hideElement(item + '_' + i + '_s');
    }
  }
  showElement(item + '_gen');
  if (answer == theanswer) {
    showHowJudged(item + '_fb', true);
    showElement(item + '_c');
    hideElement(item + '_i');
  } else {
    showHowJudged(item + '_fb', false);
    showElement(item + '_i');
    hideElement(item + '_c');
  }
  showElement(item + '_fb');
}

function cmaJudgeAlpha(item, correct, incorrect, ignoreCase) {
  var baseItem = item;

  item = item + '_1';
  var value = document.getElementById(item).value;
  var isItCorrect = false;
  if (ignoreCase) {
    value = value.toLowerCase();
  }
  for (var i = 0; i < correct.length; i++) {
    var answer = correct[i];
    if (ignoreCase) {
      answer = answer.toLowerCase();
    }
    var id = item + '_' + (i + 1) + '_cs';
    hideElement(id);
    if (value == answer) {
      isItCorrect = true;
      showElement(id);
    }
  }
  for (var i = 0; i < incorrect.length; i++) {
    var answer = incorrect[i];
    if (ignoreCase) {
      answer = answer.toLowerCase();
    }
    var id = item + '_' + (i + 1) + '_is'
    hideElement(id);
    if (value == answer) {
      showElement(id);
    }
  }
  showElement(baseItem + '_gen');
  if (isItCorrect) {
      showHowJudged(baseItem + '_fb', true);
      showElement(baseItem + '_c');
      hideElement(baseItem + '_i');
  } else {
      showHowJudged(baseItem + '_fb', false);
      showElement(baseItem + '_i');
      hideElement(baseItem + '_c');
  }
}

function cmaJudgeNumber(item, correct, incorrect, ordered) {
  var sol, insol, isCorrect, isCrap;
  var numItems = correct[0].length;
  
  var answers = new Array(numItems - 1);
  for (var i = 0; i < numItems; i++) {
    answers[i] = parseFloat(document.getElementById(item + '_' + (i + 1)).value);
    if (isNaN(answers[i])) { isCrap = true;}
  }

  if (isCrap) {
    isCorrect = false;
    sol = -1;
  } else {
    sol = testAll(answers, correct, ordered);
    isCorrect = sol > -1;
  }
  if (isCorrect) {
    document.getElementById(item + '_f').className = "feedback-correct";
    showElement(item + '_c');
    hideElement(item + '_i');
  } else {
    if (isCrap) {
      insol = -1;
    } else {
      insol = testAll(answers, incorrect, ordered);
    }
    document.getElementById(item + '_f').className = "feedback-incorrect";
    showElement(item + '_i');
    hideElement(item + '_c');
  }
  
  for (var i = 0; i < correct.length; i++){
    if (isCorrect && i == sol) {
      showElement(item + '_' + (i + 1) + '_cs');
    } else {
      hideElement(item + '_' + (i + 1) + '_cs');
    }
  }
  
  for (var i = 0; i < incorrect.length; i++){
    if (!isCorrect && i == insol) {
      showElement(item + '_' + (i + 1) + '_is');
    } else {
      hideElement(item + '_' + (i + 1) + '_is');
    }
  }

  showElement(item + '_gen');
}

function testAll(answers, data, ordered) {
  var sol, matched;
  var numItems = data[0].length;
  for (sol = 0; sol < data.length; sol++) {
    matched = true;
    for (var i = 0; i < numItems; i++) {
      if (ordered) {
        var min = data[sol][i][0];
        var max = data[sol][i][1];
       if (answers[i] < min || answers[i] > max) {
          matched = false;
          break;
        }
      } else {
        for (var j = 0; j < data[sol].length; j++) {
          var min = data[sol][j][0];
          var max = data[sol][j][1];
          if (answers[i] < min || answers[i] > max) {
            matched = false;
            break;
          }
        }
      }
      if (!matched) {
        break;
      }
    }
    if (matched) {
      return sol;
    }
  }
  
  return -1;
}

function cmaClearInput(item, numItems, numCorrect, numIncorrect) {
  for (var i = 1; i <= numItems; i++) {
    var id = item + '_' + i;
    var elem = document.getElementById(id);
    elem.value = "";

    for (var j = 1; j <= numCorrect; j++) {
      hideElement(item + '_' + j + '_cs');
    }
    for (var j = 1; j <= numIncorrect; j++) {
      hideElement(item + '_' + j + '_is');
    }

    if (i == 1) {
      elem.focus();
      hideElement(item + '_c');
      hideElement(item + '_i');
      hideElement(item + '_gen');
    }
  }
}

function cmaClearTextArea(id) {
  var elem = document.getElementById(id);
  elem.value = 'Enter your response here';
  hideElement(id + '_gen');
}

// code to enable the active control stuff to play automatically
// rather than the user having to click once to activate it
// v1.0 Copyright 2006 Adobe Systems, Inc. All rights reserved.
// modified to suit GOOD output
function AC_Generateobj(objAttrs, params, embedAttrs, alttext) { 
  var str = '<object ';
  for (var i in objAttrs) {str += i + '="' + objAttrs[i] + '" '};
  str += '>';
  for (var i in params) {str += '<param name="' + i + '" value="' + params[i] + '" />'};
  str += '<embed ';
  for (var i in embedAttrs) {str += i + '="' + embedAttrs[i] + '" '};
  str += '>';
  str += '</embed>';
  str += alttext;
  str += '</object>';

  document.write(str);
}

function AC_ParseArgs(args) {
  var ret = new Object();
  ret.objAttrs = new Object();
  ret.params = new Object();
  ret.alttext = '';
  ret.embedAttrs = new Object();

  var typeOfMedia;
  for (var i=0; i < args.length; i=i+2) {
    if (args[i].toLowerCase() == "type") {
      typeOfMedia = args[i+1];
      break;
    }
  }

  for (var i=0; i < args.length; i=i+2) {
    var currArg = args[i].toLowerCase();

    switch (currArg) {
      case "allowscriptaccess":
        ret.params[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "alttext":
        ret.alttext = args[i+1];
        break;
      case "base":
        ret.params[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "classid":
        ret.objAttrs[args[i]] = args[i+1];
        break;
      case "codebase":
        ret.objAttrs[args[i]] = args[i+1];
        break;
      case "height":
        ret.objAttrs[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "pluginspage":
        ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "src":
        if (typeOfMedia == "application/x-shockwave-flash") { ret.params["movie"] = args[i+1]; }
        if (typeOfMedia == "image/svg+xml") { ret.objAttrs["data"] = args[i+1]; }
        ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "tabindex":
        ret.objAttrs[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "type":
        ret.objAttrs[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "width":
        ret.objAttrs[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
        break;
      case "wmode":
        ret.params[args[i]] = args[i+1];
        break;
      default:
        ret.params[args[i]] = ret.embedAttrs[args[i]] = args[i+1];
    }
  }

  return ret;
}

function AC_RunContent() {
  var ret = AC_ParseArgs(arguments);
  AC_Generateobj(ret.objAttrs, ret.params, ret.embedAttrs, ret.alttext);
}
