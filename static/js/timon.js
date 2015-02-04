/*
*
* Timon.js - Joes's brother, a minimalistic javascript framework
* 
* (C)Copyright 2012 jankarelvisser@gmail.com
* All rights reserved
* Licensed under the LGPL license
* http://www.gnu.org/licenses/lgpl-3.0.txt
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
*/


function t_class(name){ return new RegExp("(^|\\s)"+name+"(\\s|$)") }
var t_id = '900', t_loaded = [], i = 0, t_included_files=[];
//set or get the id of the object
function t_set_id(obj){t_id++;id='t_'+t_id; if(obj.id){return obj.id;}try {obj.setAttribute('id',id);} catch(e){obj.id=id;}return id;}


//heavy
timon=document.getElementsByTagName("*");

//what's running
//prototype
//jquery
//mootools

function Timon(id)
{
dod=dod.getElementById(id)
Timonfy(dod.getElementsByTagName("*"));
}

function Timonfy(timon){
Timon = timon
for(i = 0;i<Timon.length;i++) 
{
//hide everything with classname hide
//open dialog
if( Timon[i].className.match(t_class('dialog')))
{
dialog=Timon[i].href;
	if(dialog)
	{
        p=dialog.split('#');
        Timon[i].href='javascript:void(0);';     
	Timon[i].setAttribute("onclick","$('#"+p[1]+"').fadeIn();");       
	}}
//close dialog
if( Timon[i].className.match('close_'))
{
	dialog=Timon[i].className.split('close_');
	target=dialog[1].split(' ');
	if(target)
	{ if(Timon[i].href){Timon[i].href='#';}
	Timon[i].setAttribute("onclick","$('#"+target[0]+"').fadeOut();");
	}}

if( Timon[i].className.match(t_class('tabs')))
	{	
//get parent nodes
	 	//Timon[i].href='#';
ie=Timon[i].children
for(item in ie)
{
console.log(ie[item])	

}

	}


if( Timon[i].className.match('set_active'))
	{//loop parentnodes	
	 	Timon[i].href='#';	
console.log(Timon[i])
 	hashChangeEventListener = setInterval("t_activemenu('"+id+"','"+list+"')", 50);
	}


if( Timon[i].className.match('nohref'))
	{	
	 	Timon[i].href='#';	
	}


if( Timon[i].className.match('window')){

linkje=Timon[i].href;Timon[i].href='javascript:void(0);';
Timon[i].setAttribute("onclick","t_popup('"+linkje+"')");

}

if( Timon[i].className.match('t_run_'))
{


}

if( Timon[i].className.match('t_function_'))
{
	
		dialog=Timon[i].className.split('t_function_');
		target=dialog[1].split(' ');
		if(target){ 
			opdracht=dialog[1].split('_');
			Timon[i].setAttribute("onclick","$('#"+opdracht[1]+"')."+opdracht[0]+"('"+opdracht[2]+"');return false;");
		}
	}

if( Timon[i].className.match('t_load_'))
{
	
		dialog=Timon[i].className.split('t_load_');
e='t_load_'+dialog[1];
                Timon[i].className.replace('.html','');
		target=dialog[1].split(' ');

		if(target){ 
			opdracht=dialog[1].split('_');

                       if(!t_loaded[opdracht[0]]){
                        t_loaded[opdracht[0]]=opdracht[1]
			$('#'+opdracht[0]).load(opdracht[1]);
			}
			
		}
	}


if( Timon[i].className.match(t_class('dropdown-toggle')))
{
	tid=t_set_id(Timon[i]);
        x=i+2; //classic bootstrap
        if(Timon[x].className.match(t_class('dropdown-menu')))
        {
            id=t_set_id(Timon[x]);
         
	//Timon[i].setAttribute("onclick","$('#"+id+"').toggleClass('show','hide');");
         Timon[i].setAttribute("onclick","t_dropdown('"+id+"','"+tid+"')");
	}
	else
	{
	x=i+1;
	 if(Timon[x].className.match(t_class('dropdown-menu')))
		{
	 id=t_set_id(Timon[x]);
         Timon[i].innerHTML=Timon[i].innerHTML+'<span class="caret"></span>';
	 Timon[i].setAttribute("onclick","t_dropdown('"+id+"','"+tid+"')");
	}
else{

 if(Timon[x].className.match(t_class('dropdown-element')))
		{
	 id=t_set_id(Timon[x]);
         Timon[i].innerHTML=Timon[i].innerHTML+'<span class="caret"></span>';
	 Timon[i].setAttribute("onclick","t_dropdown('"+id+"','"+tid+"')");
	}
else if(Timon[(x+1)].className.match(t_class('dropdown-element')))
		{
	 id=t_set_id(Timon[(x+1)]);
         Timon[i].innerHTML=Timon[i].innerHTML+'<span class="caret"></span>';
	 Timon[i].setAttribute("onclick","t_dropdown('"+id+"','"+tid+"')");
	}

else if(Timon[(x-2)].className.match(t_class('dropdown-elementx')))
		{
	 id=t_set_id(Timon[(x-2)]);
         Timon[i].innerHTML=Timon[i].innerHTML+'<span class="caret"></span>';
	 Timon[i].setAttribute("onclick","t_dropdown('"+id+"','"+tid+"')");
	}

}

	}
	}


}
}


function t_dropdown(id,tid,e){


  var posx = 0; var posy = 0; 
  if(!e){e = window.event || e.wich;}
  if (e.pageX || e.pageY){ 
    posx = e.pageX; 
    posy = e.pageY; 
  } 
  else {
    if (e.clientX || e.clientY){ 
      posx = e.clientX; 
      posy = e.clientY; 
    } 
  }
  
    g= [posx,posy]


//g=t_mouselocation(window.event)
if (g[0]-150<40){left=0}
else
{
left=g[0]-150
}
//hit it once

if($('#'+id).hasClass('nomouse')){
	//$('#'+id).css('left:'+left+'px;')
}

else if($('#'+id).hasClass('nostyle')){
	$('#'+id).css('left:'+left+'px;')
}
else {
   $('#'+id).css('left:'+left+'px; top:'+(g[1]+8)+'px')
}
	$('#'+id).toggleClass('show','hide');
	$('#'+tid).toggleClass('dropup','open');
}
/*
* Image
*
*/



/*
* m_popup
* creates an iframe
*/
function t_popup(purl)
{
	if(t_createwindow())
	{$('#m_popup').fadeIn();
	//m_opacity('m_popup',40,100,800);
	document.getElementById('m_popup_blok').innerHTML='<iframe id="m_di_pop" src='+purl+' width=100% height=100% style=border:0><\/iframe>';
	}
} 

function t_in_array(needle, haystack)
{
	for (var i = 0; i < haystack.length; i++) 
	{
        	if (haystack[i] == needle)
		{
            		return true;
        	}
	}
	return false;
}

/*
* t_createwindow
* builds the window
*/
function t_createwindow()
{
	if (!t_in_array('m_createwindow', t_included_files)) 
	{
var m_view_popup= document.createElement("div");m_view_popup.id = "m_popup";m_view_popup.style.display = "none";m_view_popup.style.opacity = 0;m_view_popup.innerHTML = '<div id="m_fade" class=\"window_background\"><\/div><div id=\"m_xx_id\"><span class=\"pointer window_close\" onclick=\"$(\'#m_popup\').fadeOut();\">&times;</strong></span><\/div><div id=\"m_popup_blok\" class=\"window_content\"><\/div>';document.body.appendChild(m_view_popup);
t_included_files[t_included_files.length] = 'm_createwindow';
		return true;    
	}
	else
	{
	return true;
	}
}



 



function timon_handler(list)
{
    var newHash = location.hash.split('#')[1];

    if(newHash != lastHash)
    {
        lastHash = newHash;
        //Do stuff!
alert(newHash)
    }
}

Timonfy(timon);