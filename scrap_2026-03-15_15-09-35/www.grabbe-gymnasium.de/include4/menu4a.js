/***
This is the menu creation code - place it right after you body tag
Feel free to add this to a stand-alone js file and link it to your page.
**/

var name   =  navigator.userAgent;
var la     = "http://www.lage-aktuell.de/";
var lp     = "pdf/lehrplan/";
var bid    = "http://www.bid-owl.de/index.php?object=";
var portal = "&access=3&doctype=portal&access=1&doctype=portal";
var gal    = "http://www2.bid-owl.de/cluster.php?object=";
var gall   = "gallery/diashow/";
var galend = "&class=3&access=1&doctype=contentframe";
var c      = "cms_hp/";
var cs     = "cms_schueler/";
var cm     = "cms_hp/musik/";
var csp    = "cms_hp/sport/";
var erg    = "cms_hp/news/";
var kunst  = "cms_hp/ausstellungen/?";
var tetr   = "cms_hp/theater/?";
var ln     = "cms_hp/lisasnews/index.php?";
var vid    = "cms_schueler/cms_video/index.php?";
var p      = "xpages/";
var tv     = "http://www.grabbe.tv/tv/"; 

//Menu object creation

oCMenu=new makeCM("oCMenu") //Making the menu object. Argument: menuname

oCMenu.frames = 1

//Menu properties
oCMenu.pxBetween=0
oCMenu.fromLeft=0
oCMenu.fromTop=105
oCMenu.rows=1
oCMenu.menuPlacement="left"

oCMenu.offlineRoot="file:///X:/"
oCMenu.onlineRoot="/"
oCMenu.resizeCheck=1
oCMenu.wait=1000
oCMenu.fillImg="cm_fill.gif"
oCMenu.zindex=0

//Background bar properties
oCMenu.useBar=0
oCMenu.barWidth="100%"
oCMenu.barHeight="menu"
oCMenu.barClass="clBar"
oCMenu.barX=0
oCMenu.barY=0
oCMenu.barBorderX=0
oCMenu.barBorderY=0
oCMenu.barBorderClass=""

//Level properties - ALL properties have to be spesified in level 0
oCMenu.level[0]=new cm_makeLevel() //Add this for each new level
oCMenu.level[0].width=126
oCMenu.level[0].height=20
oCMenu.level[0].regClass="clLevel0"
oCMenu.level[0].overClass="clLevel0over"
oCMenu.level[0].borderX=1
oCMenu.level[0].borderY=1
oCMenu.level[0].borderClass="clLevel0border"
oCMenu.level[0].offsetX=0
oCMenu.level[0].offsetY=0
oCMenu.level[0].rows=0
oCMenu.level[0].arrow=0
oCMenu.level[0].arrowWidth=0
oCMenu.level[0].arrowHeight=0
oCMenu.level[0].align="bottom"


//EXAMPLE SUB LEVEL[1] PROPERTIES
oCMenu.level[1]=new cm_makeLevel() //Add this for each new level (adding one to the number)
oCMenu.level[1].width=oCMenu.level[0].width-2
oCMenu.level[1].height=20
oCMenu.level[1].regClass="clLevel1"
oCMenu.level[1].overClass="clLevel1over"
oCMenu.level[1].borderX=1
oCMenu.level[1].borderY=1
oCMenu.level[1].align="right"
oCMenu.level[1].offsetX=-(oCMenu.level[0].width-2)/2+50
oCMenu.level[1].offsetY=0
oCMenu.level[1].borderClass="clLevel1border"


//EXAMPLE SUB LEVEL[2] PROPERTIES
oCMenu.level[2]=new cm_makeLevel() //Add this for each new level (adding one to the number)
oCMenu.level[2].width=140
oCMenu.level[2].height=20
oCMenu.level[2].offsetX=-(oCMenu.level[1].width-2)/2+40
oCMenu.level[2].offsetY=0
oCMenu.level[2].regClass="clLevel2"
oCMenu.level[2].overClass="clLevel2over"
oCMenu.level[2].borderClass="clLevel2border"

//EXAMPLE SUB LEVEL[3] PROPERTIES
oCMenu.level[3]=new cm_makeLevel() //Add this for each new level (adding one to the number)
oCMenu.level[3].width=150
oCMenu.level[3].height=20
oCMenu.level[3].offsetX=0
oCMenu.level[3].offsetY=0
oCMenu.level[3].regClass="clLevel2"
oCMenu.level[3].overClass="clLevel2over"
oCMenu.level[3].borderClass="clLevel2border"


/******************************************
Menu item creation:
myCoolMenu.makeMenu(name, parent_name, text, link, target, width, height, regImage, overImage, regClass, overClass , align, rows, nolink, onclick, onmouseover, onmouseout)
*************************************/



 oCMenu.makeMenu('top1','','&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fächer')

	oCMenu.makeMenu('sub1','top1','Musik  >','')
	  oCMenu.makeMenu('sub1027','sub1','Big Band >','')
	     oCMenu.makeMenu('sub10096','sub1027','in Concert',cm+'?Big_Band_in_Concert') 
           oCMenu.makeMenu('sub1029','sub1','Serenata Grabbiana',cm+'?Serenata_Grabbiana')	     

	  oCMenu.makeMenu('sub1030','sub1','Musical & Oper  >','')

	     oCMenu.makeMenu('sub13095','sub1030','Les Miserables',cm+'?Musical:Les_Miserables_2009')	     
	     oCMenu.makeMenu('sub13096','sub1030','Varus 2009',cm+'?Musical:Liebe_und_Verrat')
	     oCMenu.makeMenu('sub13097','sub1030','Joseph 2007',cm+'?Musical:Joseph')
	     oCMenu.makeMenu('sub13098','sub1030','Krabat 2004',p+'mu_krabat.htm')
	     oCMenu.makeMenu('sub13099','sub1030','Musik als Passion',p+'mu_passion2003.htm')

          oCMenu.makeMenu('sub1031','sub1','DJO::Orchester  >','')

	    oCMenu.makeMenu('sub14091','sub1031','Konzerte',cm+'?DJO-Konzerte')	    

       oCMenu.makeMenu('sub1032','sub1','Salonorchester >','')
          
             oCMenu.makeMenu('sub15010','sub1032','aktuell','http://www.salonorchester-detmold.de/')
             
          oCMenu.makeMenu('sub1033','sub1','Chor & Orchester I >','')
	     oCMenu.makeMenu('sub16095','sub1033','Konzerte',cm+'?Sek_1_Chor')
             oCMenu.makeMenu('sub16096','sub1033','In Dulci Jubilo',c+'sek1orch/?In_Dulci_Jubilo')
             oCMenu.makeMenu('sub16097','sub1033','Von Barock bis Pop',c+'sek1orch/?Prall_gef%FCllter_Crash-Kurs')
             oCMenu.makeMenu('sub16099','sub1033','Klosterbrunnen2003',p + 'mu_klostbrunn2003.htm')

	  oCMenu.makeMenu('sub1034','sub1','Klassenkonzerte',cm+'?Klassenkonzerte')

	  oCMenu.makeMenu('sub1035','sub1','Jugend musiziert >','')	  
	     oCMenu.makeMenu('sub17096','sub1035','Aktuelles',cm+'?Jugend_musiziert')     
 	     
	    
	    
        oCMenu.makeMenu('sub12','top1','Sport  >','')

           oCMenu.makeMenu('sub1100','sub12','Aktuelles ',csp+'')
             
         
        oCMenu.makeMenu('sub13','top1','Kunst  >','')

           oCMenu.makeMenu('sub1400','sub13','Ausstellungen',kunst)	      

           oCMenu.makeMenu('sub1410','sub13','Animation & Video',c+'kunst')
		
              
	   oCMenu.makeMenu('sub1420','sub13','Events >','')
          	oCMenu.makeMenu('sub140198','sub1420','Der Schuhrusker',kunst +'extern:Hermann_der_Schuhrusker')

	   oCMenu.makeMenu('sub1421','sub13','Performance','cms_hp/kunst/?Performance')

	oCMenu.makeMenu('sub135','top1','Philosophie>','')
	
		oCMenu.makeMenu('sub1438','sub135','Unterricht',c+'philo/philo/')
		oCMenu.makeMenu('sub1439','sub135','Essays & Clips',c+'philosophie/')

         	
	oCMenu.makeMenu('sub14','top1','weitere Fächer  >','')	
	
	
	   oCMenu.makeMenu('sub1489','sub14','Naturwissenschaft >','')
	        
		oCMenu.makeMenu('sub14876','sub1489','Naturwissenschaft',c+'wpu/?Naturwissenschaft')
		oCMenu.makeMenu('sub14877','sub1489','Chemie','chemie')
	  	oCMenu.makeMenu('sub14878','sub1489','Junge Talente',c+'informatik/?Leidenschaft:f%FCr_Chemie')
	        	  
	   oCMenu.makeMenu('sub1490','sub14','Mathe & Informatik >','')
		oCMenu.makeMenu('sub14849','sub1490','Mathematik',c+'mathe/?Welcome')
	  	oCMenu.makeMenu('sub14899','sub1490','Informatik',c+'informatik/?Automatisch_ins_Ziel')	
	  	
	    
         oCMenu.makeMenu('sub1491','sub14','Biologie >','')
		oCMenu.makeMenu('sub15098','sub1491','Jugend forscht 2007',c+'informatik/?Jugend_forscht:2007')
	      oCMenu.makeMenu('sub15099','sub1491','Stählerne Vögel',erg+'?Einmalige_Ereignisse:Riesenvogel_im_Museum')	        
 	        
 	   oCMenu.makeMenu('sub1492','sub14','Geschichte >','')
 	   
 	        oCMenu.makeMenu('sub15192','sub1492','Krieg um Troja','ppt/troja.pps')
 	        oCMenu.makeMenu('sub15193','sub1492','Die Varusschlacht',vid+'Die_Varusschlacht')
 	        oCMenu.makeMenu('sub15194','sub1492','1968','http://68er.grabbe-gymnasium.de/')
 	        oCMenu.makeMenu('sub15195','sub1492','Hitlers Aufstieg','grabbe/geschichte.htm')
	        oCMenu.makeMenu('sub15196','sub1492','Auschwitz',p+'e_gedenktag.htm')
	        oCMenu.makeMenu('sub15197','sub1492','Rollendes Detmold',p+'p_stadtfuehrung.htm')
	        oCMenu.makeMenu('sub15198','sub1492','Geschichtswettbewerb',p+'p_geschichtswettbewerb_03.htm')
	        oCMenu.makeMenu('sub15199','sub1492','Das Ruhrgebiet','ruhrgebiet/index.htm')
           
           oCMenu.makeMenu('sub1493','sub14','Deutsch>','')

		oCMenu.makeMenu('sub15291','sub1493','Bernhard Schlink',ln+'Literatur:Der_Vorleser')	   	
		oCMenu.makeMenu('sub15292','sub1493','Andreas Steinhöfel',ln+'Freizeit:Erlesenes')
	        oCMenu.makeMenu('sub15294','sub1493','Reportagen','grabbe/repo.htm')
	   	oCMenu.makeMenu('sub15295','sub1493','Kurzgeschichten','grabbe/shortstory.htm')
	   	oCMenu.makeMenu('sub15296','sub1493','6k-Geschichten',cs+'cms10/index.php')
	   	oCMenu.makeMenu('sub15297','sub1493','11er-Geschichten',c+'schreibwerkstatt/index.php')
	   	oCMenu.makeMenu('sub15298','sub1493','Analysen','grabbe/goethe.htm')
	        oCMenu.makeMenu('sub15299','sub1493','Tipps & Tricks','grabbe/rechtschreib.htm')
	        
           oCMenu.makeMenu('sub1495','sub14','Englisch >','') 

		  oCMenu.makeMenu('sub15494','sub1495','Teen Pregnancy',c+'mm_projekte/?Teenage_Pregnancy')     
		  oCMenu.makeMenu('sub15495','sub1495','Rosa Parks says NO',c+'mm_projekte/?Rosa_Parks:Movie')
	        oCMenu.makeMenu('sub15496','sub1495','The God of Small Things','http://www.godofsmallthings.de/?id=30')
	        oCMenu.makeMenu('sub15497','sub1495','War between Classes','warclass/index.html')			
	    
                
            oCMenu.makeMenu('sub1499','sub14','Religion>','')
                oCMenu.makeMenu('sub15699','sub1499','besinnliche Momente',c+'religion/?Welcome')
		           
 oCMenu.makeMenu('top2','','&nbsp;&nbsp;&nbsp;&nbsp;Lernumfeld','')


oCMenu.makeMenu('sub15','top2','Bühne  >','')

	       
                 
         oCMenu.makeMenu('sub1500','sub15','Schauspiel >','','',100,0)

 		 oCMenu.makeMenu('sub23085','sub1500','Bernarda Albas Haus',tetr + 'F%FCnf_Frauen_und_%28k%29ein_Mann')                
		 oCMenu.makeMenu('sub23086','sub1500','Currywurst',tetr + 'Currywurst_mit_Pommes')
		 oCMenu.makeMenu('sub23087','sub1500','Heiße Katze',tetr + 'Hei%DFe_Katze')
                 oCMenu.makeMenu('sub23088','sub1500','Arsen & Spitzenhäubchen',tetr + 'Eine_Prise_Gift_gef%E4llig%3F')
                 oCMenu.makeMenu('sub23089','sub1500','Hexenjagd',tetr + 'Hexenjagd')
	         oCMenu.makeMenu('sub23091','sub1500','Hase Hase',p+'th_hase.htm')
                 oCMenu.makeMenu('sub23092','sub1500','Große kleine Stadt',p+'wilder.htm')
                 oCMenu.makeMenu('sub23093','sub1500','Grabbe-Lustspiel','grabbe13/bildbogen.htm')
                 oCMenu.makeMenu('sub23099','sub1500','Loriot-Sketche','loriot/loriot.htm')

	oCMenu.makeMenu('sub1505','sub15','Varieté   >','')

	         oCMenu.makeMenu('sub24094','sub1505','Varieté_09',ln +'Abitur_2009:Variete')
	         

oCMenu.makeMenu('sub16','top2','Projekte  >','')

		
		oCMenu.makeMenu('sub1511','sub16','Eine Welt >','')
			oCMenu.makeMenu('sub24090','sub1511','Fairer Handel','http://srieche.de.tl/Eine-Welt-Projekt-am-Grabbe.htm')
		
		oCMenu.makeMenu('sub1530','sub16','Afrika >','')
		        oCMenu.makeMenu('sub24190','sub1530','Sampson erzählt',c+'hilfsaktion/index.php?Ghana-Projekt')
		        
		oCMenu.makeMenu('sub1540','sub16','Methode >','')
	       		oCMenu.makeMenu('sub24290','sub1540','Lernen lernen',p+'methode.htm')
	        oCMenu.makeMenu('sub1550','sub16','Zeitung >','')
	        	oCMenu.makeMenu('sub24389','sub1550','Schule macht Zeitung',p+'ku_schmatz.htm')
	          	oCMenu.makeMenu('sub24390','sub1550','SchmaZ_2',p+'ku_schmatz3.htm')
	          	oCMenu.makeMenu('sub24392','sub1550','Neues Jahrtausend','prowo/index.htm')
			oCMenu.makeMenu('sub24393','sub1550','Besinnungstage',bid+'112153')
	 	


oCMenu.makeMenu('sub19','top2','Lernkultur  >','')

	 
	   oCMenu.makeMenu('sub1984','sub19','Wertung der Eltern','gallery/schulwahl_2006/diashow.htm')
	   oCMenu.makeMenu('sub1985','sub19','Lesekönige',erg+'K%F6nige_und_Prinzessinnen_der_Lesekunst')	  
	   oCMenu.makeMenu('sub1986','sub19','Besinnliche Momente',c+'religion/?Schuleinstieg')	       
           oCMenu.makeMenu('sub1987','sub19','Fahrten',c+'exkursion/?Studienfahrten')	
           oCMenu.makeMenu('sub1988','sub19','Lesen fördern >','')

            oCMenu.makeMenu('sub26062','sub1988','Kooperation !',bid+'111580')
		oCMenu.makeMenu('sub26063','sub1988','Andreas Steinhöfel 1',ln + 'Welcome:Erlesenes')
		oCMenu.makeMenu('sub26064','sub1988','Andreas Steinhöfel 2','swf/steinhoefel_2007/index.htm')
		oCMenu.makeMenu('sub26065','sub1988','Willi Fährmann 1',p +'faehrmann.htm')
           	oCMenu.makeMenu('sub26066','sub1988','Willi Fährmann 2','http://hjg.freehosting.rivido.de/swf/faehrmann_2006/index.htm')
          	oCMenu.makeMenu('sub26068','sub1988','Tipps für Leseratten',p+'ku_vitrine.htm')
           	oCMenu.makeMenu('sub26069','sub1988','Lange Lesenacht',p+'lesenacht.htm')
           	
           oCMenu.makeMenu('sub1989','sub19','Gesundheit fördern >','')
	   
	        oCMenu.makeMenu('sub26297','sub1989','Wasser für alle',c+'lisas_news/?SV:Wasser_f%FCr_alle')
	        oCMenu.makeMenu('sub26298','sub1989','Gesundheitstag',erg+'Aufkl%E4rung:Gesundheit_am_Grabbe')
           	oCMenu.makeMenu('sub26299','sub1989','Über Trendgetränke',erg+'Aufkl%E4rung:Trendgetr%E4nke')

           
           oCMenu.makeMenu('sub1994','sub19','Auf der Bildungsmesse',p+'bmesse.htm')
           oCMenu.makeMenu('sub1995','sub19','Herausforderung Pisa',p+'paed_tag.htm')
           oCMenu.makeMenu('sub1996','sub19','Anti-Mobbing-Day',p+'p_mobbing.htm')
           
           oCMenu.makeMenu('sub1997','sub19','Ausbildung & Beruf',c+'beruf/?Das_Ei')           
               
           oCMenu.makeMenu('sub1998','sub19','Das ganz große Foto',p+'fototag.htm')

oCMenu.makeMenu('sub21','top2','Feste >','')

	   oCMenu.makeMenu('sub2196','sub21','Sommerfest 2007','swf/sommerfest_2007/start.htm')
	              
oCMenu.makeMenu('sub22','top2','Offene Türen >','')
	   oCMenu.makeMenu('sub2292','sub22',' 2009',erg+'?TAGE_der_OFFENEN_T%DCR:2009')
	   oCMenu.makeMenu('sub2293','sub22',' 2008',erg+'?TAGE_der_OFFENEN_T%DCR:2008')
	   oCMenu.makeMenu('sub2294','sub22',' 2007',erg+'?TAGE_der_OFFENEN_T%DCR:2007')	   
	   oCMenu.makeMenu('sub2295','sub22',' 2006',erg+'?TAGE_der_OFFENEN_T%DCR:2006')
	   oCMenu.makeMenu('sub2296','sub22',' 2005',erg+'?TAGE_der_OFFENEN_T%DCR:2005')
	   
oCMenu.makeMenu('sub23','top2','Begegnungen  >','')

	      oCMenu.makeMenu('sub2396','sub23','Israel-Austausch',erg+'?NEWS:Besuch_aus_Israel')
	      oCMenu.makeMenu('sub2397','sub23','französisch lernen',ln+'Fremdsprachen:Lernen_in_Frankreich')
	      oCMenu.makeMenu('sub2398','sub23','Schulministerin',p+'e_schaefer.htm')
	      oCMenu.makeMenu('sub2399','sub23','Comenius',erg + '?NEWS:Comenius-Projekt')	
	              

oCMenu.makeMenu('sub24','top2','AGs  >','')

	        oCMenu.makeMenu('sub2491','sub24','Liste','kontakt/ags.pdf')
		  oCMenu.makeMenu('sub2492','sub24','Videoclip','http://www.grabbe-gymnasium.de/cms_hp/kunst/?grabbe.tv:AGs_am_Grabbe')
	        oCMenu.makeMenu('sub2494','sub24','Kunst-AG Malerei',c+'ausstellungen/')
	        oCMenu.makeMenu('sub2495','sub24','Jüdischer Friedhof',ln+'Freizeit:Friedhof-AG')

oCMenu.makeMenu('sub25','top2','unterwegs >','')
	        
	        oCMenu.makeMenu('sub2599','sub25','Fahrt & Exkursion',c+'exkursion/')

oCMenu.makeMenu('sub26','top2','Sponsoren  >','')
		oCMenu.makeMenu('sub2697','sub26','Links zu Sponsoren','werbung/motto2.htm')		
		oCMenu.makeMenu('sub2698','sub26','Sparkasse Detmold','http://www.sparkasse-detmold.de/','_top')
	        

oCMenu.makeMenu('top3','','&nbsp;&nbsp;Lernen fördern')

       oCMenu.makeMenu('sub30','top3','Server  >','')

            oCMenu.makeMenu('sub3090','sub30','Schüler >','')
	      oCMenu.makeMenu('sub30095','sub3090','BiD-OWL',bid+'58636')	      
 	       
	    oCMenu.makeMenu('sub3091','sub30','Lehrer >','')
	       oCMenu.makeMenu('sub31047','sub3091','Datei ablegen',la+'phpmyexplorer/cookie1.html')
	       oCMenu.makeMenu('sub31049','sub3091','BiD-OWL',bid+'43966')	       

          oCMenu.makeMenu('sub3092','sub30','Admins >','')
	       oCMenu.makeMenu('sub31089','sub3092','Meldungen',la+'/open/pwmeldungen.htm')      
             

       oCMenu.makeMenu('sub32','top3','download area ',c+'intros/index.php?Tipps_und_Tricks') 
       oCMenu.makeMenu('sub33','top3','Schreibwerkstatt','grabbe/index.htm')

	 oCMenu.makeMenu('sub34','top3','SLZ >','')

		oCMenu.makeMenu('sub3185','sub34','Ein Wunsch erwacht',p+'slz1.htm')
		oCMenu.makeMenu('sub3186','sub34','Der Plan entsteht',bid+'111523'+portal)
		oCMenu.makeMenu('sub3187','sub34','Ideenskizze',p+'img/slz/galerie.htm')
		oCMenu.makeMenu('sub3188','sub34','Bericht in der LZ',p+'img/slz/lz_berichtx.jpg')
		oCMenu.makeMenu('sub3190','sub34','Ministerin kommt',p+'e_schaefer.htm')
		oCMenu.makeMenu('sub3191','sub34','Eröffnung',bid+'108293'+portal)
		oCMenu.makeMenu('sub3192','sub34','Videoclip','swf/slz/index.htm')
                oCMenu.makeMenu('sub3193','sub34','Besuch vom Sponsor','gallery/sparkasse_2007/index.htm')
		oCMenu.makeMenu('sub3194','sub34','Benutzungsordnung',bid+'44894'+portal)

       oCMenu.makeMenu('sub36','top3','Lernen fördern >','')

		oCMenu.makeMenu('sub3692','sub36','fördern fordern üben >','')
			oCMenu.makeMenu('sub36049','sub3692','Förderkonzept','foerderkonzept/index.php')
			oCMenu.makeMenu('sub36050','sub3692','La En Ma Phy ITG','http://www.gymnasium-karlsbad.de/ueben_und_lernen/index.php')

		oCMenu.makeMenu('sub3693','sub36','Deutsch  >','')

			oCMenu.makeMenu('sub36146','sub3693','ZUM Überblick','http://deutsch.zum.de/deutsch.html')
       			oCMenu.makeMenu('sub36147','sub3693','Ulrich Koch','http://homepage.bnv-bamberg.de/')
	       	        oCMenu.makeMenu('sub36148','sub3693','Klaus Dautel','http://www.zum.de/Faecher/D/BW/gym/hotpots/')
       		        oCMenu.makeMenu('sub36149','sub3693','Wolfgang Pollauf','http://www.zum.de/Faecher/D/BW/gym/hotpots/w_pollauf/index.htm')
		oCMenu.makeMenu('sub3694','sub36','Sprachen  >','')
        		oCMenu.makeMenu('sub36228','sub3694','Englisch','http://www.ego4u.de/')
			oCMenu.makeMenu('sub36229','sub3694','e-Latein','http://www.e-latein.de/')
		oCMenu.makeMenu('sub3695','sub36','Religion  >','')
        		oCMenu.makeMenu('sub36269','sub3695','Quiz & Rätsel','http://www.reli-on.de/werkst.htm')
		oCMenu.makeMenu('sub3696','sub36','Philosophie  >','')
        		oCMenu.makeMenu('sub36277','sub3696','Essay','http://www.learn-line.nrw.de/angebote/essaywettbewerbephilo/landeswettbewerb/essay1.htm')
			oCMenu.makeMenu('sub36278','sub3696','Schreibwerkstatt',p+'grabbe/philo.htm')                	
			oCMenu.makeMenu('sub36279','sub3696','Intelligenztest','http://de.tickle.com/test/iq/intro.html')			
		oCMenu.makeMenu('sub3697','sub36','Erdkunde  >','')
        		oCMenu.makeMenu('sub36289','sub3697','Länderquiz','http://hotpotatoes.bildung-rp.de/laenderquiz.htm')
		oCMenu.makeMenu('sub3698','sub36','Mathematik  >','')        		
			oCMenu.makeMenu('sub36299','sub3698','Logik & Konzentration','http://www.gymnasium-karlsbad.de/ueben_und_lernen/index.php')
	
	oCMenu.makeMenu('sub37','top3','Hausaufgaben >','')
		
		oCMenu.makeMenu('sub3750','sub37','Betreuung >','')
			oCMenu.makeMenu('sub37599','sub3750','Schüler Klassen 5+6','hausaufgaben/')

	
            
	oCMenu.makeMenu('sub381','top3','Spiele >','')
            oCMenu.makeMenu('sub3818','sub381','Grabbe-Puzzle',c+'intros/?Knobeln%2C_R%E4tseln%2C_Puzzeln')
            oCMenu.makeMenu('sub3819','sub381','Grabbe-Game',p+'grabbe-game.htm')
           
 oCMenu.makeMenu('top4','','&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Abitur')

     oCMenu.makeMenu('sub41','top4','2002 - 2010  >','')
		oCMenu.makeMenu('sub4104','sub41','2010 - Abivegas',ln + 'Abitur_2010')			
		oCMenu.makeMenu('sub4105','sub41','2009 - Abipedia >','','',150,0)			
			oCMenu.makeMenu('sub41054','sub4105','Gottesdienst',ln + 'Abitur_2009:Der_letzte_Tag:Gottesdienst')
			oCMenu.makeMenu('sub41055','sub4105','Entlassfeier',ln + 'Abitur_2009:Der_letzte_Tag:Entlassfeier')
			oCMenu.makeMenu('sub41056','sub4105','Abi-Ball',ln + 'Abitur_2009:Der_letzte_Tag:Abi-Ball')
			oCMenu.makeMenu('sub41057','sub4105','Abischerz','gallery/diashow/abischerz_2009.htm')
			oCMenu.makeMenu('sub41058','sub4105','Konzert',ln + 'Abitur_2009:Abi-Konzert')
			oCMenu.makeMenu('sub41059','sub4105','Variete',ln + 'Abitur_2009:Variete')

		oCMenu.makeMenu('sub4106','sub41','2008 - Abikini >','','',150,0)
					
			oCMenu.makeMenu('sub41061','sub4106','Themenlieferant',ln + 'Literatur:Der_Vorleser')
			oCMenu.makeMenu('sub41062','sub4106','Klausurgefühle',ln + 'Literatur:M%FCndliches_Abi')
			oCMenu.makeMenu('sub41063','sub4106','Abischerz',ln + 'Freizeit:Abischerz_2008')
			oCMenu.makeMenu('sub41064','sub4106','Mündliches',ln + 'Literatur:Zentralabi_2008')
			oCMenu.makeMenu('sub41065','sub4106','Mottowoche',gall + 'mottowoche_2008.htm')
			oCMenu.makeMenu('sub41066','sub4106','Entlassfeier',ln + 'Abitur_2008')
			oCMenu.makeMenu('sub41067','sub4106','Gottesdienst',gall + 'abi_fotos_2008.htm')
			oCMenu.makeMenu('sub41068','sub4106','Videoclip',ln+'Abitur_2008:Videoclip_von_Bernhard_Nowak')
		        oCMenu.makeMenu('sub41069','sub4106','Abi-Ball','http://grabbegym.gr.funpic.de/Lisa/gallery/galerie_15/diashow.htm')


		oCMenu.makeMenu('sub4107','sub41','2007 - gehen mit Stil >','','',150,0)	
	            oCMenu.makeMenu('sub41073','sub4107','Gottesdienst',gal +'199268'+ galend)
		      oCMenu.makeMenu('sub41074','sub4107','Gottesdienst-Video',vid +'Musik:Abi-Gottesdienst_2007')
			oCMenu.makeMenu('sub41075','sub4107','Entlassfeier',cm+'?Abi-Konzert:2007:Entlassfeier')			
			oCMenu.makeMenu('sub41076','sub4107','Abikonzert',cm+'?Abi-Konzert:2007')
			oCMenu.makeMenu('sub41077','sub4107','Gwennyleins Video','http://www.youtube.com/watch?v=IVva9eeVDRQ')
     	            oCMenu.makeMenu('sub41078','sub4107','Mottowoche',gal + '189198' + galend)
			oCMenu.makeMenu('sub41079','sub4107','Abischerz',cm+'?Abi-Konzert:2007:Abi-Scherz')
    
     	        oCMenu.makeMenu('sub4108','sub41','2006 - Dichte(r) gehen >','','',150,0)
     	                oCMenu.makeMenu('sub41084','sub4108','Gottesdienst 1',gal+'189281'+galend)
     	                oCMenu.makeMenu('sub41085','sub4108','Gottesdienst 2',gal+'189301'+galend)
     	                oCMenu.makeMenu('sub41086','sub4108','Entlassfeier',bid+'108380')
     	                oCMenu.makeMenu('sub41087','sub4108','Varieté',c+'variete_13/?2006')
     	                oCMenu.makeMenu('sub41088','sub4108','Abi-Konzert',bid+'108345')
		        oCMenu.makeMenu('sub41089','sub4108','Abischerz',gal+'189346'+galend)
			oCMenu.makeMenu('sub41090','sub4108','Mottowoche',gal+'205222'+galend)
		             
     			
                oCMenu.makeMenu('sub4109','sub41','2005 - bunte Vielfalt >','','',150,0)
     			oCMenu.makeMenu('sub41098','sub4109','Gottesdienst',gal+'108404'+galend)
     			oCMenu.makeMenu('sub41099','sub4109','Sexappeal',gal+'112265'+galend)
     	   		oCMenu.makeMenu('sub4110','sub41','2004 - lieben lernen',bid+'111620'+portal)     	   	
                	oCMenu.makeMenu('sub4120','sub41','2003 - leben lernen',p+'abikea.htm')
               		oCMenu.makeMenu('sub4130','sub41','2002 - fliehen lernen',p+'abicatraz.htm')
                	oCMenu.makeMenu('sub4140','sub41','Aua, Schulgong!',p+'schulgong.htm')
        
			
oCMenu.makeMenu('top5','','&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lehrpläne','')
	
    	oCMenu.makeMenu('sub51','top5','Aufgabenfeld 1 >','')

		oCMenu.makeMenu('sub5110','sub51','Deutsch >','','',150,0)
		oCMenu.makeMenu('sub5120','sub51','Englisch >','','',150,0)
			oCMenu.makeMenu('sub51201','sub5120','Sekundarstufe I',lp+'EnglischSI.pdf','_top')	
			oCMenu.makeMenu('sub51202','sub5120','Sekundarstufe II',lp+'EnglischSII.pdf','_top')

		oCMenu.makeMenu('sub5130','sub51','Französisch >','','',150,0)
			oCMenu.makeMenu('sub51301','sub5130','Sekundarstufe I',lp+'FranzoesischSI.pdf','_top')	
			oCMenu.makeMenu('sub51302','sub5130','Sekundarstufe II',lp+'FranzoesischSII.pdf','_top')
		oCMenu.makeMenu('sub5140','sub51','Spanisch >','','',150,0)
			oCMenu.makeMenu('sub51402','sub5140','Sekundarstufe II',lp+'SpanischSII.pdf','_top')
		oCMenu.makeMenu('sub5150','sub51','Latein >','','',150,0)
			oCMenu.makeMenu('sub51501','sub5150','Sekundarstufe I',lp+'LateinSI.pdf','_top')	
			oCMenu.makeMenu('sub51502','sub5150','Sekundarstufe II',lp+'LateinhSII.pdf','_top')
		oCMenu.makeMenu('sub5160','sub51','Kunst >','','',150,0)
			oCMenu.makeMenu('sub51601','sub5160','Sekundarstufe I',lp+'KunstSI.pdf','_top')	
			oCMenu.makeMenu('sub51602','sub5160','Sekundarstufe II',lp+'KunstSII.pdf','_top')
		oCMenu.makeMenu('sub5170','sub51','Musik >','','',150,0)
			oCMenu.makeMenu('sub51701','sub5170','Sekundarstufe I',lp+'MusikSI.pdf','_top')	
				
	oCMenu.makeMenu('sub52','top5','Aufgabenfeld 2 >','')  

		oCMenu.makeMenu('sub5210','sub52','Geschichte >','','',150,0)
		oCMenu.makeMenu('sub5220','sub52','Geographie >','','',150,0)
			oCMenu.makeMenu('sub52201','sub5220','Sekundarstufe I',lp+'GeographieSI.pdf','_top')	
			oCMenu.makeMenu('sub52202','sub5220','Sekundarstufe II',lp+'GeographieSII.pdf','_top')
		oCMenu.makeMenu('sub5230','sub52','Pädagogik >','','',150,0)
			oCMenu.makeMenu('sub52302','sub5230','Sekundarstufe II',lp+'PaedaSII.pdf','_top')			
		oCMenu.makeMenu('sub5240','sub52','SoWi >','','',150,0)
			oCMenu.makeMenu('sub52401','sub5240','Sekundarstufe II',lp+'SowiSII.pdf','_top')	
		oCMenu.makeMenu('sub5250','sub52','Philosophie >','','',150,0)
			oCMenu.makeMenu('sub52501','sub5250','Sekundarstufe I',lp+'PraktischePhilosophieSI.pdf','_top')	
			oCMenu.makeMenu('sub52502','sub5250','Sekundarstufe II',lp+'PhilosophieSII.pdf','_top')	
		oCMenu.makeMenu('sub5260','sub52','Politik >','','',150,0)
			oCMenu.makeMenu('sub52601','sub5260','Sekundarstufe I',lp+'PolitikSI.pdf','_top')		
		
	oCMenu.makeMenu('sub53','top5','Aufgabenfeld 3 >','') 
 		
		oCMenu.makeMenu('sub5310','sub53','Mathematik >','','',150,0)
			oCMenu.makeMenu('sub53101','sub5310','Klasse 5',lp+'Mathe5.pdf','_top')	
			oCMenu.makeMenu('sub53102','sub5310','Klasse 6',lp+'Mathe6.pdf','_top')
			oCMenu.makeMenu('sub53103','sub5310','Klasse 7',lp+'Mathe7.pdf','_top')	
			oCMenu.makeMenu('sub53104','sub5310','Klasse 8',lp+'Mathe8.pdf','_top')
			oCMenu.makeMenu('sub53105','sub5310','Klasse 9',lp+'Mathe9.pdf','_top')	
			oCMenu.makeMenu('sub53106','sub5310','Sekundarstufe II',lp+'MatheSII.pdf','_top')
		oCMenu.makeMenu('sub5320','sub53','Biologie >','','',150,0)
			oCMenu.makeMenu('sub53201','sub5320','Sekundarstufe I + II',lp+'BiologieSI_SII.pdf','_top')	
		oCMenu.makeMenu('sub5330','sub53','Chemie >','','',150,0)
			oCMenu.makeMenu('sub53301','sub5330','Sekundarstufe I',lp+'ChemieSI.pdf','_top')	
			oCMenu.makeMenu('sub53302','sub5330','Sekundarstufe II',lp+'ChemieSII.pdf','_top')	

		oCMenu.makeMenu('sub5340','sub53','Physik >','','',150,0)
			oCMenu.makeMenu('sub53402','sub5340','Sekundarstufe I + II',lp+'PhysikSISII.pdf','_top')
		oCMenu.makeMenu('sub5350','sub53','Informatik >','','',150,0)
			oCMenu.makeMenu('sub53502','sub5350','Sekundarstufe II',lp+'InformatikSII.pdf','_top')

	oCMenu.makeMenu('sub54','top5','Aufgabenfeld 4 >','')  
		
		oCMenu.makeMenu('sub5420','sub54','Religion >','','',150,0)
			oCMenu.makeMenu('sub54201','sub5420','evangelisch SI',lp+'EvReligionSI.pdf','_top')
			oCMenu.makeMenu('sub54202','sub5420','katholisch SI',lp+'katholischSI.pdf','_top')
			oCMenu.makeMenu('sub54203','sub5420','Sekundarstufe II',lp+'ReligionSII.pdf','_top')
		oCMenu.makeMenu('sub5430','sub54','Sport >','','',150,0)
			oCMenu.makeMenu('sub54301','sub5430','Sekundarstufe I',lp+'SportSI.pdf','_top')
		
		
   oCMenu.makeMenu('top6','','&nbsp;&nbsp;&nbsp;&nbsp;Organisation')

      oCMenu.makeMenu('sub55','top6','Schulprogramm','pdf/schulprogramm_2006.pdf','_top')
	oCMenu.makeMenu('sub56','top6','Hausordnung',p+'hausord.htm')
	oCMenu.makeMenu('sub57','top6','Stundentafel','pdf/Stundentafel.pdf','_top')
   	oCMenu.makeMenu('sub58','top6','Stundenraster',la+'Rubart/Stundenraster.pdf','_top')
	oCMenu.makeMenu('sub59','top6','Sprechstunden',la+'Rubart/sprechstunden.pdf')
	oCMenu.makeMenu('sub60','top6','Ansprechpartner',la+'Rubart/aufgaben.pdf')
	
   
     oCMenu.makeMenu('sub67','top6','Service >','')  

	oCMenu.makeMenu('sub6500','sub67','SV','cms_10/svgg/')  
	oCMenu.makeMenu('sub6510','sub67','Formulare',p+'grabform.htm')
	oCMenu.makeMenu('sub6520','sub67','Satellitenbild','cms_hp/news/?Satellitenbild_der_Schule') 
	oCMenu.makeMenu('sub6530','sub67','Wegskizze',erg +'?Satellitenbild_der_Schule')       
	oCMenu.makeMenu('sub6540','sub67','Namensgeber!','http://gutenberg.spiegel.de/index.php?id=19&autorid=213&autor_vorname=+Christian+Dietrich&autor_nachname=Grabbe&cHash=b31bbae2c6' ,'_top')
      oCMenu.makeMenu('sub6550','sub67','Schulgeschichte','xpages/geschichte.htm')        
      oCMenu.makeMenu('sub6560','sub67','Kalender gefällig?',p+'kalender.htm')		          
	oCMenu.makeMenu('sub6570','sub67','Facharbeit',c+'intros/index.php?Tipps_und_Tricks:Facharbeit:Maschineschreiben')     
	              
        
     oCMenu.makeMenu('sub68','top6','Mittelstufe',la+'Mittelstufe/')     
       
     oCMenu.makeMenu('sub69','top6','Personalia >','')	   
	   
	   oCMenu.makeMenu('sub6985','sub69','Erfolgreiche Ex',c+'die_ehemaligen/?Welcome')
           oCMenu.makeMenu('sub6986','sub69','Die Assistenten',ln+'Fremdsprachen:Die_Assistenten')
           oCMenu.makeMenu('sub6987','sub69','Grabbe-Schüler','http://www.stayfriends.de/s/18982/Nordrhein-Westfalen/Detmold/Gymnasium/Christian-Dietrich-Grabbe-Gymnasium.html')
           
           oCMenu.makeMenu('sub6990','sub69','Unvergessene Lehrer',erg+'?Schulleitung:Unvergessene_Kollegen')   


oCMenu.makeMenu('top7','','&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Kontakt')
        
	    oCMenu.makeMenu('sub7086','top7','So finden Sie uns',erg +'?Satellitenbild_der_Schule')
          oCMenu.makeMenu('sub7087','top7','Fon Fax E-Mail',p+'kontakte.html')
	    oCMenu.makeMenu('sub7088','top7','Gästebuch','http://www.246253.multiguestbook.com/')
	    oCMenu.makeMenu('sub7092','top7','Schulpflegschaft',erg +'?Schulpflegschaft:Kontakt')
	    oCMenu.makeMenu('sub7093','top7','Schulkonferenz','kontakt/schulkonferenz.pdf')       
          oCMenu.makeMenu('sub7094','top7','Förderverein',p+'beamer.htm')
          oCMenu.makeMenu('sub7095','top7','Ansprechpartner',la+'Rubart/aufgaben.pdf')
          oCMenu.makeMenu('sub7096','top7','Partnerschulen',p+'partner.htm')
	    oCMenu.makeMenu('sub7097','top7','Impressum',p+'impressum.html')
          oCMenu.makeMenu('sub7098','top7','Webmaster',p+'email.htm')
          oCMenu.makeMenu('sub7099','top7','Ehemalige','http://www.stayfriends.de/s/18982/Nordrhein-Westfalen/Detmold/Gymnasium/Christian-Dietrich-Grabbe-Gymnasium.html')
	    oCMenu.makeMenu('sub7100','top7','SV','cms_10/svgg/')  


//Leave this line - it constructs the menu
oCMenu.construct()