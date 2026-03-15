/******************************************************************************
* File: md8lib.js                                                             *
*                                                                             *
* Copyright MatchWare A/S                                                     *
* Author: Jens Ø. Nielsen                                                     *
******************************************************************************/


var clickobj  = null;
var insideobj = null;
var actions   = new Array();
var terminating = false;
var initialized = false;
var animatingobjs = new Array();
var nextanimation = 0;
var bIsIE4Final = false;
var currentHttpReq = null

var LocalVar = new Array();
var localvarcount = 0;

var m_bIsTop = false;


function IsIE() {
	return navigator.userAgent.indexOf("MSIE") > -1;
}

//*****************************************************************************
//** Variable Handling
//*****************************************************************************

function Var(name, value) {
 this.name = name;
 this.value = value;
}

function GetSystemVar(sVarName)
{
	if (sVarName == "@cursorxpos") {
		return (window.event.x+document.body.scrollLeft)
	}
	if (sVarName == "@cursorypos") {
		return (window.event.y+document.body.scrollTop)
	}
	if (sVarName == "@date") {
		var dNow = new Date();
		return dNow.toDateString();
	}
	if (sVarName == "@dateday") {
		var dNow = new Date();
		return dNow.getDate();
	}
	if (sVarName == "@datemonth") {
		var dNow = new Date();
		return dNow.getMonth();
	}
	if (sVarName == "@dateyear") {
		var dNow = new Date();
		return dNow.getFullYear();
	}
	if (sVarName == "@screenxsize") {
		return window.screen.width;
	}
	if (sVarName == "@screenysize") {
		return window.screen.height;
	}
	if (sVarName == "@time") {
		var dNow = new Date();
		return dNow.toTimeString();
	}
	if (sVarName == "@timehour") {
		var dNow = new Date();
		return dNow.getHours();
	}
	if (sVarName == "@timemin") {
		var dNow = new Date();
		return dNow.getMinutes();
	}
	if (sVarName == "@timesec") {
		var dNow = new Date();
		return dNow.getSeconds();
	}

	// @WindowsDir
	// @DesktopDir
	// @DocDir
	// @WindowsDir
	// @SystemDir
	// @TempDir
	// @Timer
	// @ProgramDir
	// @CPU
	// @Key
	// @OS
	// @PageCount
	// @PageName
	// @PageNum
	// @PageRange
	// @ColorBits
	// @Colors

	return sVarName + " is not supported";
}

function GetVar(sVarName)
{
	if (sVarName.charAt(0) == "@") {
		return GetSystemVar(sVarName);
	}

	// Check for local var
	var nIndex = GetVarIndex(sVarName);
	if (nIndex != null)
		return LocalVar[nIndex].value;
	
	// Check for global var
	var globalvar = GetTop().global.globalvar;
	nIndex = globalvar.GetVarIndex(sVarName)
	if (nIndex != null)
		return globalvar.LocalVar[nIndex].value;
	
	alert("error : variable " + sVarName + " is not defined");
	return null;
}

function GetVarIndex(sVarName)
{
	for (var n=0; n<localvarcount; n++) {
		if (LocalVar[n].name == sVarName)
			return n;
	}
	return null;
}

function AssignVar(sVarName, nVarValue)
{
	LocalVar[localvarcount] = new Var(sVarName, nVarValue);
	localvarcount++;
}



function SetVar(sVarName, nVarValue)
{
	// Check for local var
	var nIndex = GetVarIndex(sVarName);
	if (nIndex != null) {
		var oldval = LocalVar[nIndex].value;
		if ( typeof( oldval) == "number")
			LocalVar[nIndex].value = parseFloat( nVarValue);
		else if ( typeof( oldval) == "string")
			LocalVar[nIndex].value = String( nVarValue);
		else		
			LocalVar[nIndex].value = nVarValue;
		return;
	}


	// Check for global var
	var globalvar = GetTop().global.globalvar;
	var nIndex = globalvar.GetVarIndex(sVarName);
	if (nIndex != null) {
		var oldval = globalvar.LocalVar[nIndex].value;
		if ( typeof( oldval) == "number")
			globalvar.LocalVar[nIndex].value = parseFloat( nVarValue);
		else if ( typeof( oldval) == "string")
			globalvar.LocalVar[nIndex].value = String( nVarValue);
		else		
			globalvar.LocalVar[nIndex].value = nVarValue;
		return;
	}
	
}

function HttpRequestAction(sUrl, sData, sVerb, sResponseVar, sStatusCodeVar, sStatusTextVar, sOkActionNames, sErrorActionNames)
{
	this.Start = HttpRequestAction_Start;
	this.sUrl = sUrl;
	this.sData = sData;
	this.sVerb = sVerb;
	this.sResponseVar = sResponseVar;
	this.sStatusCodeVar = sStatusCodeVar;
	this.sStatusTextVar = sStatusTextVar;
	this.sOkActionNames = sOkActionNames;
	this.sErrorActionNames = sErrorActionNames;
}

function HttpRequestAction_Start()
{
	currentHttpReq = this;
	
	var postDoc = GetTop().global.globalpost;
	
	var url1 = eval(this.sUrl);
	url1 = url1.toLowerCase();
	if (url1.substring(0,4) == "http") {
		var url2 = document.location.href;
		url2 = url2.toLowerCase();
		var nPos = url1.indexOf("/", 7);
		if (url2.length >= nPos && url1.substring(0,nPos) == url2.substring(0,nPos)) {
		} else {
			alert("Error: You need to make the http request to the same domain as the script is running on.");
			return;
		}
	}

	var sHtml = "<html>\n<head>\n</head>\n<body>\n";
			
	sHtml += "<form method=\""+this.sVerb+"\" id=\"reqForm\" action=\""+eval(this.sUrl)+"\">\n";
			
	var strData = eval(this.sData);
	
	var arr = strData.split("&");
	for (var n=0; n<arr.length; n++) {
		var ar = arr[n].split("=");
		if (ar.length != 2) {
			alert("Error in data string : " + strData)
			return;
		}
		sHtml += "<input type=\"hidden\" name=\"" + ar[0] + "\" value=\"" +ar[1] + "\">\n";
	}	

	sHtml += "</form>\n";
	sHtml += "</body>\n</html>\n";
	
	postDoc.document.write(sHtml);
	postDoc.document.getElementById( "reqForm").submit();
}

function HttpRequestDone(sUrl, sContent)
{
	if (!currentHttpReq)
		return;
	SetVar(currentHttpReq.sResponseVar, sContent);
	if (sUrl == eval(currentHttpReq.sUrl)) {
		HttpRequestOk(currentHttpReq);
	} else {
		HttpRequestError(currentHttpReq);
	}
	currentHttpReq = null;
}

function HttpRequestOk(obj)
{
	SetVar(obj.sStatusCodeVar, "200");
	SetVar(obj.sStatusTextVar, "Success");
	var arr = obj.sOkActionNames.split(";");
	for (n = 0; n<arr.length-1; n++) {
		var sAction = "actions."+arr[n] + ".Start();";
		eval(sAction);
	}
}

function HttpRequestError(obj)
{
	SetVar(obj.sStatusCodeVar, "400");
	SetVar(obj.sStatusTextVar, "Error");
	var arr = obj.sErrorActionNames.split(";");
	for (n = 0; n<arr.length-1; n++) {
		var sAction = "actions."+arr[n] + ".Start();";
		eval(sAction);
	}
}


//*****************************************************************************
//** Set/Get Property Action
//*****************************************************************************

function SetPropertyAction(sObjectName, sObjectType, sPropertyName, sPropertyValue)
{
	this.sObjectType = sObjectType;			// Objects type
	this.sObjectName = sObjectName;			// Objects name
	this.propertyname = sPropertyName;		// Property name
	this.propertyvalue = sPropertyValue;	// Propertyvalue / expression
	this.Start = SetPropertyAction_Start;	
}

function SetPropertyAction_Start()
{
	var sProperty = GetObjectPropertyName(this.sObjectName, this.sObjectType, this.propertyname);
	if (sProperty == null)
		return;
	
	if (this.sObjectType == "InputObject" && this.propertyname == "value") {
		var EnableDecimals = eval(this.sObjectName + "_JSGinner.EnableDecimals");
		if (EnableDecimals == 1) {
				
			var DecimalPoint = eval(this.sObjectName + "_JSGinner.DecimalPoint");
			var Decimals = eval(this.sObjectName + "_JSGinner.Decimals");	
			sVal = ConvertFromStringToValue(eval(this.propertyvalue), DecimalPoint, Decimals);
			
			//alert(this.propertyvalue)
			
			eval(sProperty + " = \"" + sVal + "\";");
			
			return;
		}
	}
	eval(sProperty + " = " + this.propertyvalue + ";");
}

function ConvertFromStringToValue(sValue, DecimalPoint, Decimals)
{
	sValue = "" + sValue;
	
	if (sValue.indexOf(DecimalPoint) > -1)
		sValue = sValue.replace(DecimalPoint, ".");

	var	n = parseFloat(sValue);
	
	if (!n) n = 0;
	
	sValue = n.toFixed(Decimals);

	if (sValue.indexOf(".") > -1)
		sValue = sValue.replace(".", DecimalPoint);
	
	return sValue;
}

function GetObjectProperty(objname, objtype, prop)
{
	var sProperty = GetObjectPropertyName(objname, objtype, prop);
	if (sProperty == null)
		return;
		
		if (objtype == "InputObject" && prop == "value") {
			var EnableDecimals = eval(objname + "_JSGinner.EnableDecimals");
			if (EnableDecimals == 1) {
				var DecimalPoint = eval(objname + "_JSGinner.DecimalPoint");
				var Decimals = eval(objname + "_JSGinner.Decimals");	
				return parseFloat(ConvertFromStringToValue(eval(sProperty), DecimalPoint, Decimals));
			}
		}
	
	if (prop == "x" || prop == "y" || prop == "width" || prop == "height") {
		return parseInt(eval(sProperty));
	}
		
		
	return eval(sProperty);
}

function GetObjectPropertyName(objname, objectType, property)
{
	if (objectType == "InputObject") {
		var sObjectProperty = "";
		if (property == "text")
			sObjectProperty = objname + "_JSGinner.value";
			
		if (property == "value") {
			sObjectProperty = objname + "_JSGinner.value";
		}
			
		if (property == "x") {
			sObjectProperty = objname + ".style.left";
		}
		if (property == "y") {
			sObjectProperty = objname + ".style.top";
		}
		if (property == "width") {
			sObjectProperty = objname + "_JSGinner.style.width";
		}
		if (property == "height") {
			sObjectProperty = objname + "_JSGinner.style.height";
		}
		if (property == "backgroundcolor") {
			sObjectProperty = objname + "_JSGinner.style.backgroundColor";
		}
		if (property == "textcolor") {
			sObjectProperty = objname + "_JSGinner.style.color";
		}
		if (sObjectProperty == "")
			return;
		return sObjectProperty;
	}
}

//*****************************************************************************
//** If Then Else Action
//*****************************************************************************

function IfThenElseAction(sExp, sTrueActions, sFalseActions)
{
	this.sExp = sExp;
	this.sTrueActions = sTrueActions;
	this.sFalseActions = sFalseActions;
	this.Start = IfThenElseAction_Start;
}

function IfThenElseAction_Start()
{
	if (eval(this.sExp)) {
		eval(this.sTrueActions);
	} else {
		eval(this.sFalseActions);
	}
}

//*****************************************************************************
//** Assign Action
//*****************************************************************************

function AssignAction(sVar, sValue)
{
	this.m_sVar = sVar;
	this.m_sValue = sValue;
	this.Start = AssignAction_Start;
}

function AssignAction_Start()
{
	SetVar(this.m_sVar, eval(this.m_sValue))
}

//*****************************************************************************
//** Page Action
//*****************************************************************************

function PageAction( pagename) {

 this.m_PageName = pagename;
 this.Start = PageAction_Start;
}

function PageAction_Start() {

	var top = GetTop();

 if ( this.m_PageName == "") return;
 if ( this.m_PageName == "@prepage") {
   window.history.back();
 }
 else {
   if ( parent != self) {
     if ( top.global.advbookmark) {
       var url = top.location.href;
       var len = url.indexOf( "?",0);
       if ( len > 0)
         url = url.substring( 0,len);
       url += "?" + this.m_PageName + PAGE_ACTION_POST_FIX;
       terminating = true;
       top.location = url;
       return;
     }
   }
   terminating = true;
   location = this.m_PageName + PAGE_ACTION_POST_FIX;
 }
}




function IsNetscape() {
 
 if ( navigator.appName != "Netscape") return false;
 if ( parseInt(navigator.appVersion) < 4) return false;
 if ( parseInt(navigator.appVersion) > 4) return false;
 return true;
}

function IsNetscape6() {
 
 if ( navigator.appName != "Netscape") return false;
 if ( parseInt(navigator.appVersion) < 5) return false;
 return true;
}

function IsMac() {
 return navigator.userAgent.indexOf("Mac") > -1;
}

function IsOldBrowser() {

 var agent = navigator.userAgent;
 if ( agent.substring( 0,7) != "Mozilla") return false;
 var verpos = agent.indexOf( "/")+1;
 if ( verpos < 0) return false;
 agent = agent.substring( verpos,verpos+2);
 var m_ver = parseInt( agent);
 return m_ver < 4;
}

function FrameIt( page) {

 terminating = true;
 window.location = "index.htm?" + page;
}

//------------------------------------

var ANIM_TICK = 50;

var ANIM_STYLE_NORMAL   = 0;
var ANIM_STYLE_FIRSTPOS = 1;
var ANIM_STYLE_FLYTO    = 2;
var ANIM_STYLE_FLYFROM  = 3;

//------------------------------------


//------------------------------------

function bsearch(myarray, val) {

  var lo=0;
  var hi=myarray.length;

  while(true) {
    var mid=Math.floor((hi+lo)/2);
    if(mid==0)
      return mid;
    if(mid==myarray.length-1)
      return mid-1;
    else if((myarray[mid]<=val && myarray[mid+1]>val))
      return mid;               
    else if(val<myarray[mid])
      hi=mid;
    else
      lo=mid;
  }
  return 0;
}


/******************************************************************************
* Class AnimationPath                                                         *
******************************************************************************/

function AnimationPath(xpoints_array, ypoints_array) {

  this.m_xpoints_array=xpoints_array;
  this.m_ypoints_array=ypoints_array;
  this.m_sqdists=new Array(xpoints_array.length);
  this.m_sqdistsum=0;

  this.GetPointAtTime=AnimationPath_GetPointAtTime;

  /*********************/ 
  var x=xpoints_array[0];
  var y=ypoints_array[0];

  for(i=0; i<this.m_sqdists.length; i++) {
    var dx = this.m_xpoints_array[i]-x;
    var dy = this.m_ypoints_array[i]-y;
    this.m_sqdistsum += Math.sqrt(dx*dx+dy*dy);
	this.m_sqdists[i] = this.m_sqdistsum;

    x=xpoints_array[i];
    y=ypoints_array[i];
  }

}

function AnimationPath_GetPointAtTime(t) {

  if(t>=1) {
    var endx=this.m_xpoints_array[this.m_xpoints_array.length-1];
    var endy=this.m_ypoints_array[this.m_ypoints_array.length-1];
    return new Array(endx, endy);
  }
  
  var pos = t*this.m_sqdistsum;
  var idx = bsearch(this.m_sqdists, pos);
  
  var dx  = this.m_xpoints_array[idx+1] - this.m_xpoints_array[idx];
  var dy  = this.m_ypoints_array[idx+1] - this.m_ypoints_array[idx];
   

  var dv  = pos - this.m_sqdists[idx];     /* distance we went too far */
  var lenseg = this.m_sqdists[idx+1]-this.m_sqdists[idx];

  dx*=(dv/lenseg);
  dy*=(dv/lenseg);

  xpos=this.m_xpoints_array[idx]+dx;
  ypos=this.m_ypoints_array[idx]+dy;

  return new Array(xpos, ypos);
}


/******************************************************************************
* Class AnimationAction                                                       *
******************************************************************************/

function AnimationAction( myname,obj,path,totaltime,repeat,reverse,autoshow,style) {

  this.m_name=myname;
  this.m_object= FindObject( obj);
  this.m_path=path;
  this.m_totaltime=totaltime;
  this.m_time=0;
  this.m_paused=false;
  this.m_startdate=null;
  this.m_repeat=repeat;
  this.m_reverse=reverse;
  this.m_style=style;
  this.m_autoshow = autoshow;
  this.m_doshow = this.m_autoshow;
  this.m_timerid = 0;
  
  this.Start = AnimationAction_Start;
  this.Stop  = AnimationAction_Stop;
  this.Pause = AnimationAction_Pause;
  this.Tick  = AnimationAction_Tick;
}

function FindAnimation( objname) {

 for ( var i = 0; i < nextanimation;i++) {
   if ( animatingobjs[ i].m_object == objname)
     return i;
 }
 return -1;
}

function RemoveAnimation( objname) {

 var i = FindAnimation( objname);
 if ( i >= 0) {
   animatingobjs[ i] = null;
   nextanimation--;
   for ( ; i < nextanimation; i++)
     animatingobjs[ i] = animatingobjs[ i+1];
 }
}


function AnimationAction_Start() { 

 var i = FindAnimation( this.m_object);
 if ( i >= 0) {
   animatingobjs[ i].Stop();
 }
 else
   animatingobjs[ nextanimation++] = this;

 if ( IsObjVisible( this.m_object))
   this.m_doshow = false;
 else
   this.m_doshow = this.m_autoshow;

 var obj_x = GetObjLeft( this.m_object) + GetObjWidth( this.m_object) / 2;
 var obj_y = GetObjTop( this.m_object) + GetObjHeight( this.m_object) / 2;
 if ( ! this.m_paused) { // !paused => anim from start 
   this.m_time=0;
   this.m_startdate=new Date();
   var endidx=this.m_path.m_xpoints_array.length-1;
   if ( this.m_style == ANIM_STYLE_NORMAL) {
	   this.m_offset_x=0;
	   this.m_offset_y=0;
   }
   else if ( this.m_style == ANIM_STYLE_FLYTO) {
     var endpoint = this.m_reverse ? 0 : endidx;
	   this.m_offset_x = obj_x - this.m_path.m_xpoints_array[endpoint];
     this.m_offset_y = obj_y - this.m_path.m_ypoints_array[endpoint];
   }
   else if ( this.m_style == ANIM_STYLE_FLYFROM) {
     var startpoint = this.m_reverse ? endidx : 0;
	   this.m_offset_x = obj_x - this.m_path.m_xpoints_array[ startpoint];
	   this.m_offset_y = obj_y - this.m_path.m_ypoints_array[ startpoint];
   }
   else if ( this.m_style == ANIM_STYLE_FIRSTPOS) {
	   this.m_seg0_x = obj_x;
	   this.m_seg0_y = obj_y;
     startpoint = this.m_reverse ? endidx : 0;
     this.m_seg0_dx = this.m_path.m_xpoints_array[ startpoint]-this.m_seg0_x;
     this.m_seg0_dy = this.m_path.m_ypoints_array[ startpoint]-this.m_seg0_y;
  
     this.m_seg0_len=Math.sqrt(this.m_seg0_dx*this.m_seg0_dx + this.m_seg0_dy*this.m_seg0_dy);
     this.m_seg0_endtime= this.m_seg0_len / (this.m_seg0_len+this.m_path.m_sqdistsum);
   }
 }
 else {               // paused
   this.m_startdate=new Date();
   paused=false;
 }

 this.m_timerid = window.setTimeout( "actions." + this.m_name + ".Tick()", ANIM_TICK);
}


function AnimationAction_Tick() {

 if ( terminating) return;
 this.m_timerid = 0;
 if(this.m_startdate!=null) {
   var datenow=new Date();
   var msnow=this.m_time + (datenow-this.m_startdate);
   var t=msnow/this.m_totaltime;
   if ( t > 1) t = 1;
   if ( this.m_style != ANIM_STYLE_FIRSTPOS) {
     if(this.m_reverse)
       t=1-t;
     point = this.m_path.GetPointAtTime(t);
     var x = point[0] + this.m_offset_x - GetObjWidth( this.m_object) / 2;
     var y = point[1] + this.m_offset_y - GetObjHeight( this.m_object) / 2;
     SetObjPosition( this.m_object,x,y);
   }
   else { 
     // firstpos hack
     if(t < this.m_seg0_endtime) {
       var tt= t*(1/this.m_seg0_endtime);
       var x = this.m_seg0_x+tt*this.m_seg0_dx - GetObjWidth( this.m_object) / 2;
       var y = this.m_seg0_y+tt*this.m_seg0_dy - GetObjHeight( this.m_object) / 2;
       SetObjPosition( this.m_object,x,y);
     }
     else {
       var tt=(t-this.m_seg0_endtime)*(1/(1-this.m_seg0_endtime));
       if(this.m_reverse)
         tt=1-tt;
       point=this.m_path.GetPointAtTime(tt);
       var x = point[ 0] - GetObjWidth( this.m_object) / 2;
       var y = point[ 1] - GetObjHeight( this.m_object) / 2;
       SetObjPosition( this.m_object,x,y);
     }
   }

   if(msnow<this.m_totaltime)     
     this.m_timerid = window.setTimeout( "actions." + this.m_name+".Tick()", ANIM_TICK);
   else if(this.m_repeat) {
     this.m_startdate=new Date();
     this.m_timerid = window.setTimeout( "actions." + this.m_name + ".Tick()", ANIM_TICK);
   }
   else {
     RemoveAnimation( this.m_object);
   }
 }
 if ( this.m_doshow) {
   ShowObject( this.m_object,true);
   this.m_doshow = false;
 }
}

function AnimationAction_Stop() {

 RemoveAnimation( this.m_object);
 this.m_paused=false; 
 this.m_time=0;
 if ( this.m_timerid) {
   clearTimeout( this.m_timerid);
   this.m_timerid = 0;
 }
}

function AnimationAction_Pause() {

  this.m_paused=true;
  d= new Date();
  this.m_time+=d-this.m_startdate;
  this.m_startdate=null;
}

//------------------------------------

function TimeLineAction( myname, actionarray,delayarray) {

 this.m_Name       = myname;
 this.m_ActionList = actionarray;
 this.m_DelayList  = delayarray;
 this.m_Current    = 0;
 this.m_TimerId    = 0;

 this.Start = TimeLineAction_Start;
 this.Tick  = TimeLineAction_Tick;
}


function TimeLineAction_Start() {

 if ( this.m_ActionList.length == 0) return;
 if ( this.m_TimerId) 
   clearTimeout( this.m_TimerId);
 this.m_Current = 0;
 this.m_TimerId = window.setTimeout( "actions." + this.m_Name+".Tick()", this.m_DelayList[ 0]);
}


function TimeLineAction_Tick() {

 this.m_TimerId = 0;
 if ( terminating) return;
 var index = this.m_Current;
 this.m_ActionList[ index].Start();
 if ( this.m_Current != index) return;
 this.m_Current++;
 if ( this.m_Current >= this.m_ActionList.length) return;
 this.m_TimerId = window.setTimeout( "actions." + this.m_Name+".Tick()", this.m_DelayList[ this.m_Current]);
}


//------------------------------------

function EmailAction( to,subject,text) {
 
 this.m_To      = to;
 this.m_Subject = subject;
 this.m_Text    = text;

 this.Start = EmailAction_Start;
}

function EmailAction_Start() {
	var txt = eval(this.m_Text)
	var txt = escape(txt);
	// Hack to get the euro sign to work
	while (txt.indexOf("%u20AC") > -1)
		txt = txt.replace("%u20AC", "%80");
	window.location.href = "mailto:" + eval(this.m_To) + "?Subject=" + eval(this.m_Subject) + "&Body=" + txt;
}

//------------------------------------

function HttpAction( url,innewwindow) {

 this.m_Url         = url;
 this.m_InNewWindow = innewwindow;

 this.Start = HttpAction_Start;
}

function HttpAction_Start() {
 if ( this.m_InNewWindow) {
    window.open( eval(this.m_Url));
 } 
 else
   GetTop().location.href = eval(this.m_Url);
}

//------------------------------------

function StartAction( action) {

 this.m_Action = action;

 this.Start = StartAction_Start;
}

function StartAction_Start() {

 eval( this.m_Action);
}

var isns6 = IsNetscape6();

function BrowserInit() {
}

function GetObjLeft( obj) {
  return isns6 ? parseInt( obj.style.left) : obj.style.pixelLeft;
}

function GetObjTop( obj) {
  return isns6 ? parseInt( obj.style.top): obj.style.pixelTop;
}

function GetObjWidth( obj) {
 if ( isns6) 
   return parseInt( obj.style.width);
 if ( obj.style.pixelWidth)
   return obj.style.pixelWidth;
 else
   return obj.clientWidth;
}

function GetObjHeight( obj) {
 if ( isns6) 
   return parseInt( obj.style.height);
 if ( obj.style.pixelHeight)
   return obj.style.pixelHeight;
 else
   return obj.clientHeight;
}

function SetObjPosition( obj,left,top) {

 if ( isns6) {
   obj.style.left = left;
   obj.style.top  = top;
 }
 else {
   obj.style.pixelLeft = left;
   obj.style.pixelTop  = top;
 }
}

function IsObjVisible( obj) {
 return obj.style.visibility == "visible";
}

function ShowObject( obj,visible) {
 obj.style.visibility = visible ? "visible" : "hidden";
}

function FindObject( name) {
 if ( bIsIE4Final)
   return document.all( name);
 else
   return document.getElementById( name);
}

//------------------------------------

var PAGE_ACTION_POST_FIX = ".htm";

//------------------------------------

var effects = new Array();
effects.BoxIn      = 0;
effects.BoxOut     = 1;
effects.CircleIn   = 2;
effects.CircleOut  = 3;
effects.WipeUp     = 4;
effects.WipeDown   = 5;
effects.WipeRight  = 6;
effects.WipeLeft   = 7;
effects.HorzBlinds = 9;
effects.Dissolve        = 12;
effects.SplitVerticalIn = 13;
effects.Normal          = 100;
effects.Fade            = 101;

//------------------------------------

function HideAction( obj,duration,effecttype) {

 this.m_Obj        = FindObject( obj);
 this.m_Duration   = duration;
 this.m_EffectType = effecttype;

 this.Start = HideAction_Start;
}


function HideAction_Start() {

 if ( this.m_Obj.style.visibility == "hidden") return;
 if ( isns6) {
  this.m_Obj.style.visibility = "hidden";
  return;
 }
 switch ( this.m_EffectType) {
  case effects.Normal :
    this.m_Obj.style.visibility = "hidden";
    break;
  case effects.Fade :
    this.m_Obj.style.filter = "blendTrans(duration=" + (this.m_Duration / 1000) + ")";
    this.m_Obj.filters.blendTrans.stop();
    this.m_Obj.filters.blendTrans.apply();
    this.m_Obj.style.visibility="hidden";
    this.m_Obj.filters.blendTrans.play();
    break;
  default :
    this.m_Obj.style.filter = "revealTrans(duration==" + (this.m_Duration / 1000) + ", transition=" + this.m_EffectType + ")";
    this.m_Obj.filters.revealTrans.stop();
    this.m_Obj.filters.revealTrans.apply();
    this.m_Obj.style.visibility="hidden";
    this.m_Obj.filters.revealTrans.play();
    break;
 }
}

//------------------------------------


function ShowAction( obj,duration,effecttype) {

 this.m_Obj        = FindObject( obj);
 this.m_Duration   = duration;
 this.m_EffectType = effecttype;

 this.Start = ShowAction_Start;
}


function ShowAction_Start() {

 if ( this.m_Obj.style.visibility == "visible") return;
 if ( isns6) {
  this.m_Obj.style.visibility = "visible";
  return;
 }

 switch ( this.m_EffectType) {
  case effects.Normal :
    this.m_Obj.style.visibility = "visible";
    break;
  case effects.Fade :
    this.m_Obj.style.filter = "blendTrans(duration=" + (this.m_Duration / 1000) + ")";
    this.m_Obj.filters.blendTrans.stop();
    this.m_Obj.filters.blendTrans.apply();
    this.m_Obj.style.visibility = "visible";
    this.m_Obj.filters.blendTrans.play();
    break;
  default :
    this.m_Obj.style.filter = "revealTrans(duration==" + (this.m_Duration / 1000) + ", transition=" + this.m_EffectType + ")";
    this.m_Obj.filters.revealTrans.stop();
    this.m_Obj.filters.revealTrans.apply();
    this.m_Obj.style.visibility = "visible";
    this.m_Obj.filters.revealTrans.play();
    break;
 }
}

//------------------------------------

function SoundAction( sound,repeat,cancelmidi,cancelwave) {

 var pos = sound.lastIndexOf( ".");
 var ext = sound.substring( pos).toLowerCase();

 this.m_Sound      = sound;
 this.m_Repeat     = repeat;
 this.m_CancelMidi = cancelmidi;
 this.m_CancelWave = cancelwave;
 this.m_Midi       = ext == ".mid";

 this.Start = SoundAction_Start;
}

function SoundAction_Start() {

	var globalsound = GetTop().global.globalsound;

	if ( window.parent == self) return;

	if ( this.m_CancelMidi) 
		globalsound.StopMidi();
		
	if ( this.m_CancelWave) 
		globalsound.StopWave();

	if ( this.m_Sound == "") return;

	if (this.m_Midi) {
		globalsound.StartMidi(this.m_Repeat, this.m_Sound);
	} else {
		globalsound.StartWave(this.m_Repeat, this.m_Sound);
	}
}

//------------------------------------

function MsgBoxAction(sText)
{
	this.m_sText = sText;
	this.Start = MsgBoxAction_Start;
}

function MsgBoxAction_Start()
{
	alert(eval(this.m_sText));
}


function SetCursorAction( type) {

 this.m_Type = type;

 this.Start = SetCursorAction_Start;
}


function SetCursorAction_Start() {

 var aDivs = GetTags("DIV");
 if ( ! aDivs) return;

 for ( var i=0;i < aDivs.length; i++) 
   aDivs[i].style.cursor = this.m_Type;

 aDivs = GetTags("IMG");
 if ( ! aDivs) return;

 for ( var i=0;i < aDivs.length; i++) 
   aDivs[i].style.cursor = this.m_Type;

 aDivs = GetTags("INPUT");
 if ( ! aDivs) return;

 for ( var i=0;i < aDivs.length; i++) 
   aDivs[i].style.cursor = this.m_Type;
}

function GetTags(sTagType)
{
	if (isns6) {
		return document.getElementsByTagName(sTagType)
	} else {
		return document.body.all.tags(sTagType);
	}
}

//------------------------------------

function N6Button( id) {
 if ( ! isns6) return;
 var obj = FindObject( id + "_JSGinner");
 var b = parseInt( obj.style.borderWidth)*2;
 obj.style.width = parseInt( obj.style.width) - b;
 obj.style.height = parseInt( obj.style.height) - b;
}

function TextObject_GetText(textobj)
{
	return textobj.value;
}

function TextObject_PutText(textobj, text)
{
	textobj.value = text;
}

function GetTop()
{
	if (this.m_bIsTop == null) {
		return null;
	}
	if (this.m_bIsTop == true) {
		return this;
	}
	if (this == parent) {
		return this;
	} 
	return parent.GetTop();
}


function RND(nMin, nMax)
{
	return Math.floor(Math.random()*(nMax-nMin+1)) + nMin;
}

function ABS(n)
{
	return Math.abs(n);
}

function COS(n)
{
	return Math.cos(n);
}

function FLOAT(n)
{
	n = parseFloat(n);
	if (isNaN(n))
		return 0;
	return n;
}

function INT(n)
{
	n = parseInt(n);
	if (isNaN(n))
		return 0;
	return n;
}

function STRING(n)
{
	return n.toString();
}

function LEN(str)
{
	return str.length;
}

function LOWER(str)
{
	return str.toLowerCase();
}

function UPPER(str)
{
	return str.toUpperCase();
}

function NOT(n)
{
	return !n;
}

function SIN(n)
{
	return Math.sin(n);
}

function SUBPOS(str1, str2)
{
	return str1.indexOf(str2)+1;
}

function SUBSTR(str, nStart, nLength)
{
	return str.substr(nStart-1,nLength);
}

function SQR(n)
{
	return Math.sqrt(n);
}

function FORMAT(nValue, sFormat)
{
	var sValue = nValue.toString();
	if (sFormat == null)
		return sValue;
		
	nDotPos = sFormat.indexOf(".");
	
	var nZeros = 0;	// Before dot
	var n2 = 0;	// value after dot
	var s3 = "";	// letter after dot
	
	if (nDotPos == -1) {
		s3 = sFormat;
	} else {
		var s = sFormat.substring(0, nDotPos);
		if (s != "")
			nZeros = parseInt(s);
		sFormat = sFormat.slice(nDotPos+1);
		s3 = sFormat.charAt(sFormat.length-1);
		sFormat = sFormat.slice(0,-1);
		if (sFormat.length > 0)
			n2 = parseInt(sFormat);
			
			
	}
	if (s3 == "")
		s3 = "g";	// default : use "g"
		
		
	if (s3 == "g" || s3 == "G") {
		if (parseFloat(nValue) / 100000 > 1) {	// more that 6 significant digits
			s3 = "e";
		} else {
			s3 = "f";
		}
	}

//	alert(nZeros + " : " + n2 + " : " + s3);

	var sReturn = sValue;
	
	if (s3 == "e" || s3 == "E") {

		

		var n = parseFloat(sValue);
		var nFactor = 0;
		while (n > 10) {
			nFactor++;
			n = n / 10;
		}
			
		sReturn = sValue.charAt(0);
		sValue = sValue.slice(1);
				
		if (n2 > 0) {
			sReturn += ".";
		}
				
		while (n2 > 0) {
			if (sValue.length == 0) {
				sReturn += "0";
			} else {
				if (sValue.charAt(0) == ".")
					sValue = sValue.slice(1);
				sReturn += sValue.charAt(0);
				sValue = sValue.slice(1);
			}
			n2--;
		}
		
		if (nZeros != 0) {
			if (nZeros > 0) {
				while (sReturn.length < nZeros)
					sReturn = "0" + sReturn;
			} else {
				nZeros = -nZeros;
				while (sReturn.length < nZeros)
					sReturn = sReturn + "0";
		
			}
		}

		sReturn += s3;
		
		var s = nFactor.toString();
		while (s.length < 3)
			s = "0" + s;
			
		sReturn += " + " + s;
	}

	if (s3 == "f" || s3 == "F") {
		if (n2 == 0) {
			var nPos = sValue.indexOf(".");
			if (nPos > -1) {
				n2 = 6-nPos;
			}
		}
		
		var n = parseFloat(sValue)
		sReturn = n.toFixed(n2);
		
		if (nZeros != 0) {
			if (nZeros > 0) {
				while (sReturn.length < nZeros)
					sReturn = "0" + sReturn;
			} else {
				nZeros = -nZeros;
				while (sReturn.length < nZeros)
					sReturn = sReturn + "0";
		
			}
		}
	}

	return sReturn;
}

function donothing() {}

function IEPNGAlpha( img) {

	if ( ! IsIE()) return;
	img.onload = donothing;
	var dir = img.src;
	var pos = dir.lastIndexOf( "/");
	if ( pos < 0)
		pos = dir.lastIndexOf( "\\");
	dir = dir.substr( 0,pos+1);
	var imageurl = img.src;
	img.src = dir + "transparent.gif";
	img.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+imageurl+"',sizingMethod='scale');";
}

function DummyAction() {

	this.Start = DummyAction_Start;
}

function DummyAction_Start() {

}