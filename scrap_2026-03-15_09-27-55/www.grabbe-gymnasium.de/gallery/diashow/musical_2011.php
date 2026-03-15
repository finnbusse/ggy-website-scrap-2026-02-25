<html><head>
<title>Grabbe-Gymnasium</title>
<meta http-equiv=expires content=0>
<link rel=stylesheet type=text/css href=style.css>
</head>

<script language=JavaScript><!--

var server = '../galerie_78/';
var i = 0;
var nullen = '00';

// hier die Bilderzahl einstellen
var bilderzahl = 90;

var aPic = new Array();
while (i < bilderzahl)
  {
  if (i < 9) { nullen = '00' } else {nullen = '0' };  	
  if (i > 98) { nullen = '' };
  aPic[i] = server + nullen + (i+1) + '.JPG';
  i++;
  }

var iSpeed = 2.9;
var iFade = 2.9;
var bRunning = true;
var iTimeOut;
var iPicLen = aPic.length;
var j = -1;

var aLoad = new Array();
for (i = 0; i < iPicLen; i++){ aLoad[i] = new Image() }

function fLoadPix() {
  if(!document.picArr) document.picArr = new Array();
  var i,j = document.picArr.length;
  var a = fLoadPix.arguments;
  for(i=0; i<a.length; i++) {
    if (a[i].indexOf('#')!=0) {
      document.picArr[j] = new Image;
      document.picArr[j++].src=a[i]; } } }

function fShowPic(iPic) {
  if (document.all){
    document.images.animation.style.filter='blendTrans(duration=iFade)';
    document.images.animation.filters.blendTrans.Apply();
    document.images.animation.src = aLoad[iPic].src;
    document.images.animation.filters.blendTrans.Play();
    document.all.pictext.innerText = 'Image ' + (iPic + 1);
  } else {
    document.getElementById('animation').src = aLoad[iPic].src;
    document.getElementById('pictext').innerHTML = 'Image ' + (iPic + 1); } }

function fRun(){
  j++;
  if (j > (iPicLen-1)) j=0;
  aLoad[j].src = aPic[j];
  fShowPic(j);
  iTimeOut = setTimeout('fRun()', iSpeed * 1000); }

function fControl() {
  if (bRunning) { bRunning = false;
    clearTimeout(iTimeOut);
    document.ctlstartstop.src = '../images/gstart.gif'; }
  else { bRunning = true;
    document.ctlstartstop.src = '../images/gpause.gif';
    iTimeOut = setTimeout('fRun()', 1); } }

function fGoFirst() {
  j = -1;
  clearTimeout(iTimeOut);
  bRunning = true;
  document.ctlstartstop.src = '../images/gpause.gif';
  iTimeOut = setTimeout('fRun()', 1); }

function fGoNext() {
  j++;
  if (j > (iPicLen-1)) j=0;
  aLoad[j].src = aPic[j];
  fShowPic(j);
  bRunning = false;
  clearTimeout(iTimeOut);
  document.ctlstartstop.src = '../images/gstart.gif'; }

function fGoPrev() {
  j--;
  if (j==-1) j=(iPicLen-1);
  aLoad[j].src = aPic[j];
  fShowPic(j);
  bRunning = false;
  clearTimeout(iTimeOut);
  document.ctlstartstop.src = '../images/gstart.gif'; }

function tag1() {
  j = -1;
  clearTimeout(iTimeOut);
  bRunning = true;
  document.ctlstartstop.src = '../images/gpause.gif';
  iTimeOut = setTimeout('fRun()', 1); }


function tag2() {
  j = 44;
  clearTimeout(iTimeOut);
  bRunning = true;
  document.ctlstartstop.src = '../images/gpause.gif';
  iTimeOut = setTimeout('fRun()', 1); }



function tag3() {
  j = -1;
   clearTimeout(iTimeOut);
  bRunning = true;
  document.ctlstartstop.src = '../images/gpause.gif';
  iTimeOut = setTimeout('fRun()', 1); }



function tag4() {
  j = -1;
   clearTimeout(iTimeOut);
  bRunning = true;
  document.ctlstartstop.src = '../images/gpause.gif';
  iTimeOut = setTimeout('fRun()', 1); }



function tag5() {
  j = -1;
   clearTimeout(iTimeOut);
  bRunning = true;
  document.ctlstartstop.src = '../images/gpause.gif';
  iTimeOut = setTimeout('fRun()', 1); }




//--></script>

</head>

<body onload=fLoadPix('../images/gstart.gif','../images/gpause.gif');fRun() topmargin=0 leftmargin=0>

<center>

<table border=0 cellpadding=0 cellspacing=0 width=800>
   <tr>

   <td colspan=12 bgcolor='steelblue' align='center' height='24'><br><h4><font color='white'>Madame Musicauds: Schüler führen eigenständig inszeniertes Musical auf</h4></td>
   </tr>

     <!-- Bildtext -->
     <td id=pictext align=left height=6 width=100></td>

     <!-- Index -->
     <td align=center height=6 width=10></td>
          
	    <!-- Tag 0 -->
	    <td align=center height=6 width=130>
		<a href=javascript:tag1(); onFocus=if(this.blur)this.blur()>
		Fotos:<br>Sabine Hilbert-Opitz</a></td>


          
	    <!-- Tag 1 -->
	   
<td align=center height=6 width=130>
		<a href=javascript:tag2(); onFocus=if(this.blur)this.blur()>
		Film:<br> Hunger/Gärtner</a></td>

</td>

	    <!-- Tag 2 -->
	    <td align=center height=6 width=60><a href="/cms_hp/musik/?Musical:Madame_Musicauds_2011:Videoclip"><img src='../images/VIDEOKAMk.gif' border='0'> </a></td>
           </td>


	    <!-- Tag 3 -->
	    <td align=center height=6 width=70>
<p><span style='line-height:25px;font-family:futura,verdana;font-weight:bold;font-size:11px;color:#336699'>2515</span><br><b><font size="-2"><font color="#336699">Besucher&nbsp;&nbsp;</font></font></b>
</td>

</td>

	    <!-- Tag 4 -->
	    <td align=center height=6 width=80>
		<img src="loading.gif"</a></td>



</td>

	    <!-- Tag 5 -->
	    <td align=center height=6 width=10>&nbsp;</td>



	    <!-- First -->
          <td align=center height=6 width=40>
          <a href=javascript:fGoFirst(); onFocus=if(this.blur)this.blur()>
          <img name=ctlgofirst src=../images/gfirst.gif alt='First' style='border-width: 0' width= 20  height= 20 ></a></td>

          <!-- Prev -->
          <td align=center height=6 width=40>
          <a href=javascript:fGoPrev(); onFocus=if(this.blur)this.blur()>
          <img name=ctlgoprev src=../images/gprev.gif alt='Back' style='border-width: 0' width= 20  height= 20 ></a></td>

          <!-- Next -->
          <td align=center height=6 width=40>
          <a href=javascript:fGoNext(); onFocus=if(this.blur)this.blur()>
          <img name=ctlgonext src=../images/gnext.gif alt='Next' style='border-width: 0' width= 20  height= 20 ></a></td>

          <!-- Controller -->
          <td align=center height=6 width=40>
          <a href=javascript:fControl(); onFocus=if(this.blur)this.blur()>
          <img name=ctlstartstop src=../images/gpause.gif alt='Start / Pause' style='border-width: 0' width= 20  height= 20 ></td>

   </tr>
   <tr><td height=10 colspan=12 bgcolor='steelblue'></td></tr>
   <tr><td valign=top align=center colspan=12 bgcolor='steelblue'>

   <!--- PIC --->
   <img id=animation border=0 src='transparent.gif' style='border-width: 0'>
   <!--- PIC --->

   </td></tr>
   <tr><td height=5 colspan=12 bgcolor='steelblue'></td></tr>
   <tr><td height=16 colspan=12>

   <table border=0 cellpadding=0 cellspacing=0 width=100% height='30' bgcolor='steelblue'>
   <tr><td align=left width=33%><font size='-2' color='#c0c0c0'>created by hjg<br>22.01.2011</td>
   <td width=34% align=left></td>
   <td width=33% align=right>
<object type="application/x-shockwave-flash" data="/gallery/diashow/sound/emff_easy_glaze.swf" width="110" height="34">
 <param name="movie" value="/gallery/diashow/sound/emff_easy_glaze.swf">
<param name="bgcolor" value="#4682b4">
<param name="FlashVars" value="src=/gallery/diashow/sound/col.mp3&amp;autostart=yes">
</object>
</td>
   </tr></table></td></tr>

</table>
<center>

</body></html>
