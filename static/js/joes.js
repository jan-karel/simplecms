/*
* Joes.js - a minimalistic javascript framework
* 
* (C)Copyright 2013 jankarelvisser@gmail.com
* All rights reserved
* Licensed under the LGPL license
* http://www.gnu.org/licenses/lgpl-3.0.txt
*
* 
*
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
*/


//check for unbootstrap else import animate.css

//required vars and value;s
var is_id = /^#([\w\-]+)$/, is_class = /^\.([\w\-]+)$/, is_html = /^[^<]*(<.+>)[^>]*$/, lege_array = [], cached_items = [], selector_type = false, j_id = 100, j_ie_hell, j_included_files = [], j_included_files_external = [], ajax_results = [], req = [], i = 0;
var html5elements = ['address', 'article', 'aside', 'audio', 'canvas', 'command', 'datalist', 'details', 'dialog', 'figure', 'figcaption', 'footer', 'header', 'hgroup', 'keygen', 'mark', 'meter', 'menu', 'nav', 'progress', 'ruby', 'section', 'time', 'video'];  
var html4elements = ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'font', 'small', 'sup', 'img', 'ul', 'li', 'ol', 'form', 'legend', 'fieldset', 'input', 'select', 'button|script', 'title', 'rel']; 
var Joes = window.Joes = function( selector, context ) {return this instanceof Joes ? this.drama( selector, context ) : new Joes( selector, context ); };
if ( typeof J === "undefined" ){window.J = Joes;}if ( typeof jQuery === "undefined" ){window.jQuery = Joes;  window.$ = Joes;}



//hck ie
if (/MSIE (\d+\.\d+);/.test(navigator.userAgent)){ j_ie_hell = new Number(RegExp.$1);  if (j_ie_hell<9){for (i in html5elements ){document.createElement(html5elements[i]);}}}

//set or get the id of the object
function j_set_id(obj){j_id++;id='j_'+j_id; if (obj.id){return obj.id;} try {obj.setAttribute('id',id);} catch(e){obj.id=id;}return id;}

//set attribute on object
function j_set_attr(obj,attr,val){obj.setAttribute(attr,val);}

function j_in_array(needle, haystack){for ( i = 0; i < haystack.length; i++) {if (haystack[i] === needle){return true;}}return false;}

function j_has_class(needle, haystack, return_method){var teller = 0,classes = [];for (i = 0; i < haystack.length; i++) {if (haystack[i].className.match(new RegExp('(\\s|^)'+needle+'(\\s|$)'))){ classes[teller++]= (return_method === 'id'?(haystack[i].id || j_set_id(haystack[i])):haystack[i]);}	}return classes;}

function j_add(content,type,id){id=id || 'mi_'+(j_id++);if(type){j_view_append=document.createElement(type);j_view_append.id = id;if(type!='input'){j_view_append.innerHTML = content;}else{j_view_append.type = content;}document.body.appendChild(j_view_append);return id;}else{return document.createTextNode(content);}}


function j_selector(selector, return_method)
{
var elem=[];
//enter browser wonderland
//quickly handle id's and classes

			if(typeof(selector) === "function")
			{
				selector();return false;
			}
			else if(selector.match(is_id))
			{
			
				elem = (return_method==='id'?(m(selector.replace('#','')) ? [selector.replace('#','')]:false): m(selector.replace('#','')));
			
				
			}
			
			else if(selector==='document' || selector==='window' || selector==='body')
			{
		
				elem=document.body;
			}
			else if (selector.match(is_class))
			{
					//always get the latest
					elem=j_has_class(selector.replace('.',''),document.getElementsByTagName("*"),return_method);
					
			
			}


			else if (j_in_array(selector,html4elements) || j_in_array(selector,html5elements))
			{
					//always get the latest
		if (j_ie_hell<8)
		{					
			var stack = [Array().slice.call(document.getElementsByTagName("body")[0].childNodes)]
                        alert(stack)		
			var list=document.getElementsByTagName(selector);
					
			if(list.length===1)
		        {
                                        
					elem=[j_set_id(list)];
					
					}
					else
					{
                                         if(list){ 
					elem.push(list);}
					}

	       }
					else
					{
                                           
						//elem=Array.prototype.slice.call(document.getElementsByTagName(selector));
                        elem=Array.prototype.slice.call(document.querySelectorAll(selector));
					    
					}
					
					if(return_method==='id')
					{
						var teller = 0, newelem = [];
						for(i=0; i < elem.length; i++){newelem[teller++] = elem[i].id || j_set_id(elem[i]);} elem=newelem;
					}
				
			
				
			
			}
			else
			{
				
				var teller = 0, newelem = [];
				elem=Array.prototype.slice.call(document.querySelectorAll(selector));
					if(return_method==='id')
					{
						for(i=0; i < elem.length; i++){newelem[teller++] = elem[i].id || j_set_id(elem[i]);}
                                                elem=newelem;
					}
					
			
			}
			
	return elem;
}

//ajax
Joes.ajax = Joes.prototype = j_ajax;
Joes.get = Joes.prototype = j_ajax_get;
Joes.post = Joes.prototype = j_ajax_post;

function m(id){
if(id.id){return document.getElementById(id.id)}
else{return document.getElementById(id);}}

Joes.fn = Joes.prototype = {

	drama: function( selector, context ) {
		// Make sure that a selection was provided
		selector = selector || document;
		
		//get document items
		//this string will be cleaned
		this.current_value=null;
		this.prev_value=null;
		this.current_postition=null;
                this.prev_position=null;
			if(selector !== document)
			{	
	                  q=j_register('selector_'+selector);
                          if(q===null)
			   {    
				var elem = j_selector(selector,'id');
				this.item_collection = (elem || false);			
				this.selector_used=selector;
				this.length = (elem.length || 1);
                                j_register('selector_'+selector,this);
                           }
                           else {
                           

				this.item_collection = q.item_collection;			
				this.selector_used=q.selector_used;
				this.current_value=q.current_value;
				this.length=q.length;}
			}
			
			return this;
		
		},


	change:function(a,b)
	{
	return this;
	},		
		
	cache:function(id,value)
	{
	
	},
		
	find:function(id,value)
	{
	
	},	
		
	closest:function(id,value)
	{
	
	},	
		
	children:function(id,value)
	{
	
	},	
		
	next:function(id,value)
	{
	
	},

		
	previous:function(id,value)
	{
	
	},

    //calback function 			
	uitvoeren: function(callback)
		{var elemx = [];for(i=0; i < this.item_collection.length; i++){elemx+=callback(m(this.item_collection[i]));}return elemx;},
	each:function(callback)
		{this.uitvoeren(callback);return this;},
	bind: function(a,b)
		{return this.each(function(el){j_event(a,b,el);});},
	unbind: function(a)
		{return this;},
	click: function(a)
		{return this.bind('click',a);},
	load: function(a,b)
		{j_ajax_get(a,this.item_collection[0],b);},

	attr: function(name,value){
      return (typeof name === 'string' && value === 'undefined') ?  m(this.item_collection[0]).getAttribute(name) || undefined  :
        this.each(function(el){
          if (typeof name === 'object') {for(k in name) {el.setAttribute(k, name[k]);}}
          else {el.setAttribute(name,value);}
        });
    },
    
   data: function(name, value){
      return  (typeof name === 'string' && value === 'undefined') ?  this.attr('data-' + name) : m(this.item_collection[0]).setAttribute('data-'+name,value);
    },
    
    val: function(formval){
   return formval === void 0 ? m(this['item_collection'][0]).value : m(this['item_collection']).value  = formval;
    },
    html: function(formval){

   return formval === void 0 ? m(this['item_collection'][0]).innerHTML : m(this['item_collection'][0]).innerHTML  = formval;
    },
    
    id:function(){return this.item_collection[0];},
    obj:function() {return m(this.id());},
    /*return left, right */
    position: function()
    {var e= j_position(this.obj());if(!e){e = [this.obj().offsetLeft, this.obj().offsetTop];}return e;},
  
	
	
css: function(stijl){return this.each(function(el){el.style.cssText += ';'+stijl;});},
css_overwrite: function(stijl){return this.each(function(el){el.style.cssText = stijl;});},
removedrop: function () {this.each(function(el){el.removeAttribute("ondrop");el.removeAttribute("ondragenter");
el.removeAttribute("ondragover");});return this;},
removedrag: function () {this.each(function(el){el.removeAttribute("draggable");el.removeAttribute("ondragstart");});return this;},
drag: function (dragcallback) {this.each(function(el){el.setAttribute("draggable","true");el.setAttribute("ondragstart",(dragcallback || "j_drag(this,event)"));});return this;},
drop: function (dropcallback) {this.each(function(el){el.setAttribute("ondrop",(dropcallback || "j_drop(this, event)"));el.setAttribute("ondragenter","return false");el.setAttribute("ondragover","return false");});return this;},
snap: function () {this.each(function(el){el.setAttribute("ondragenter","j_drop(this, event)");});return this;},
ondrop: function () {this.each(function(el){el.setAttribute("ondrop","j_drop(this, event)");el.setAttribute("ondragenter","return false");el.setAttribute("ondragover","return false");});return this;},

//requires animate.css
//Attention seekers
flash: function () { j_csseffect(this.id, 'flash');return this.addClass('flash animated');},
bounce: function () {j_csseffect(this.id, 'bounce');return this.addClass('bounce animated');},
shake: function () {j_csseffect(this.id, 'shake');return this.addClass('shake animated');},
tada: function () {j_csseffect(this.id, 'tada');return this.addClass('tada animated');},
swing: function () {j_csseffect(this.id, 'swing');return this.addClass('swing animated');},
wobble: function () {j_csseffect(this.id, 'wobble');return this.addClass('wobble animated');},
wiggle: function () {j_csseffect(this.id, 'wiggle');return this.addClass('wiggle animated');},
pulse: function () {j_csseffect(this.id, 'pulse');return this.addClass('pulse animated');},
//Flippers
flip: function () {j_csseffect(this.id, 'flip');return this.addClass('flip animated');},
flipInX: function () {j_csseffect(this.id, 'flipInX');return this.addClass('flipInX animated');},
flipOutX: function () {j_csseffect(this.id, 'flipOutX');return this.addClass('flipOutX animated');},
flipInY: function () {j_csseffect(this.id, 'flipInY');return this.addClass('flipInY animated');},
flipOutY: function () {j_csseffect(this.id, 'flipOutY');return this.addClass('flipOutY animated');},
//Fading entrances
//fadeIn: function () {return this.addClass('fadeIn animated');},
fadeInUp: function () {j_csseffect(this.id, 'fadeInUp');return this.addClass('fadeInUp animated');},
fadeInDown: function () {j_csseffect(this.id, 'fadeInLeft');return this.addClass('fadeInLeft animated');},
fadeInRight: function () {j_csseffect(this.id, 'fadeInRight');return this.addClass('fadeInRight animated');},
fadeInUpBig: function () {j_csseffect(this.id, 'fadeInUpBig');return this.addClass('fadeInUpBig animated');},
fadeInDownBig: function () {j_csseffect(this.id, 'fadeInDownBig');return this.addClass('fadeInDownBig animated');},
fadeInLeftBig: function () {j_csseffect(this.id, 'fadeInLeftBig');return this.addClass('fadeInLeftBig animated');},
fadeInRightBig: function () {j_csseffect(this.id, 'fadeInRightBig');return this.addClass('fadeInRightBig animated');},
//Fading exits
//fadeOut: function () {return this.addClass('fadeOut animated');},
fadeOutUp: function () {j_csseffect(this.id, 'fadeOutUp');return this.addClass('fadeOutUp animated');},
fadeOutDown: function () {j_csseffect(this.id, 'fadeOutDown');return this.addClass('fadeOutDown animated');},
fadeOutLeft: function () {j_csseffect(this.id, 'fadeOutLeft');return this.addClass('fadeOutLeft animated');},
fadeOutRight: function () {j_csseffect(this.id, 'fadeOutRight');return this.addClass('fadeOutRight animated');},
fadeOutUpBig: function () {j_csseffect(this.id, 'fadeOutUpBig');return this.addClass('fadeOutUpBig animated');},
fadeOutDownBig: function () {j_csseffect(this.id, 'fadeOutDownBig');return this.addClass('fadeOutDownBig animated');},
fadeOutLeftBig: function () {j_csseffect(this.id, 'fadeOutLeftBig');return this.addClass('fadeOutLeftBig animated');},
fadeOutRightBig: function () {j_csseffect(this.id, 'fadeOutRightBig');return this.addClass('fadeOutRightBig animated');},
//Bouncing entrances
bounceIn: function () {j_csseffect(this.id, 'bounceIn');return this.addClass('bounceIn animated');},
bounceInDown: function () {j_csseffect(this.id, 'bounceInDown');return this.addClass('bounceInDown animated');},
bounceInUp: function () {j_csseffect(this.id, 'bounceInUp');return this.addClass('bounceInUp animated');},
bounceInLeft: function () {j_csseffect(this.id, 'bounceInLeft');return this.addClass('bounceInLeft animated');},
bounceInRight: function () {j_csseffect(this.id, 'bounceInRight');return this.addClass('bounceInRight animated');},
//Bouncing exits
bounceOut: function () {j_csseffect(this.id, 'bounceOut');return this.addClass('bounceOut animated');},
bounceOutDown: function () {j_csseffect(this.id, 'bounceOutDown');return this.addClass('bounceOutDown animated');},
bounceOutUp: function () {j_csseffect(this.id, 'bounceOutUp');return this.addClass('bounceOutUp animated');},
bounceOutLeft: function () {j_csseffect(this.id, 'bounceOutLeft');return this.addClass('bounceOutLeft animated');},
bounceOutRight: function () {j_csseffect(this.id, 'bounceOutRight');return this.addClass('bounceOutRight animated');},
//Rotating entrances
rotateIn: function () {j_csseffect(this.id, 'rotateIn');return this.addClass('rotateIn animated');},
rotateInDownLeft: function () {j_csseffect(this.id, 'rotateInDownLeft');return this.addClass('rotateInDownLeft animated');},
rotateInDownRight: function () {j_csseffect(this.id, 'rotateInDownRight');return this.addClass('rotateInDownRight animated');},
rotateInUpLeft: function () {j_csseffect(this.id, 'rotateInUpLeft');return this.addClass('rotateInUpLeft animated');},
rotateInUpRight: function () {j_csseffect(this.id, 'rotateInUpRight');return this.addClass('rotateInUpRight animated');},
//Rotating exits
rotateOut: function () {j_csseffect(this.id, 'rotateOut');return this.addClass('rotateOut animated');},
rotateOutDownLeft: function () {j_csseffect(this.id, 'rotateOutDownLeft');return this.addClass('rotateOutDownLeft animated');},
rotateOutDownRight: function () {j_csseffect(this.id, 'rotateOutDownRight');return this.addClass('rotateOutDownRight animated');},
rotateOutUpLeft: function () {j_csseffect(this.id, 'rotateOutUpLeft');return this.addClass('rotateOutUpLeft animated');},
rotateOutUpRight: function () {j_csseffect(this.id, 'rotateOutUpRight');return this.addClass('rotateOutUpRight animated');},
//Lightspeed
lightSpeedIn: function () {j_csseffect(this.id, 'lightSpeedIn ');return this.addClass('lightSpeedIn animated');},
lightSpeedOut: function () {j_csseffect(this.id, 'lightSpeedOut');return this.addClass('lightSpeedOut animated');},
//Specials
hinge: function () {j_csseffect(this.id, 'hinge');return this.addClass('hinge animated');},
rollIn: function () {j_csseffect(this.id, 'rollIn');return this.addClass('rollIn animated');},
rollOut: function () {j_csseffect(this.id, 'rollOut');return this.addClass('rollOut animated');},
	
//old skool
hide: function () {return this.css('display:none');},
show: function () {return this.css('display:block');},
fadeIn: function (speed) {return this.each(function(el){j_fade_in(el);});},
fadeOut: function (speed) {return this.each(function(el){j_fade_out(el);});},
toggle: function () {
this.each(function(el){
if(j_hasclass(el, 'hide')){m(el).className.replace('hide','show');}
else if(j_hasclass(el, 'show')){m(el).className.replace('show','hide');}
else {
if(el.style.cssText.match('display: none')){el.style.cssText.replace('display: none','display: block')}else{el.style.cssText += ';display: none'}	
}});	
},

slideToggle: function () {this.show();		
},
hasClass: function (cls) {for (i=0; i < this.item_collection.length; i++){if(this.item_collection[i]){if(j_hasclass(this.item_collection[i],cls)){ return true;}}return false;}},
addClass: function (cls) {for (i=0; i < this.item_collection.length; i++){if(this.item_collection[i]){if(!j_hasclass(this.item_collection[i],cls)){ m(this.item_collection[i]).className += " "+cls;}}}return this;},
removeClass: function (cls) {var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');for(i=0; i < this.item_collection.length; i++){if(this.item_collection[i]){if(j_hasclass(this.item_collection[i],cls)){m(this.item_collection[i]).className=m(this.item_collection[i]).className.replace(reg,' ');}}}return this;},
toggleClass:function(target,cls)
{
	var targettest = new RegExp('(\\s|^)'+target+'(\\s|$)');
	var clstest = new RegExp('(\\s|^)'+cls+'(\\s|$)');

	for(i=0; i < this.item_collection.length; i++)
		{if(this.item_collection[i]){
			if(j_hasclass(this.item_collection[i],target)){
				m(this.item_collection[i]).className=m(this.item_collection[i]).className.replace(targettest,' '+cls);
			}
			else if(j_hasclass(this.item_collection[i],cls))
			{
				m(this.item_collection[i]).className=m(this.item_collection[i]).className.replace(clstest,' '+target);
			}
			else
			{
			m(this.item_collection[i]).className+= " "+target;
			}
			}
		}
	return this;
	}

}

function j_csseffect(id, eff){
    window.setTimeout( function(){
			J('#'+id).removeClass(eff+' animated');},
			1300		);
}
function j_drag(drop_target, e) {e.dataTransfer.setData('Text', drop_target.id);	}
function j_drop(drop_target, e) {var id = e.dataTransfer.getData('Text');drop_target.appendChild(m(id));e.preventDefault();}
function j_hasclass(obj,cls){return m(obj).className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));}	
function j_appear(target,content,duration){j_fade_out(target,(duration || 500));
setTimeout("j_('"+target+"').innerHTML=\""+content+"\";j_fade_in('"+target+"','"+(duration || 500)+"');",(duration || 500));}
function j_show(target){m(target).style.display = "block";}
function j_hide(target) {m(target).style.display = "none";}
function j_fade_out(target,duration){if(typeof target === 'object'){target=j_set_id(target);}
j_opacity(target,90,10,700);setTimeout("j_hide('"+target+"')",(duration || 500)); return false;}
function j_fade_in(target,duration){if(typeof target === 'object'){target=j_set_id(target);}
m(target).style.opacity=0;j_show(target);j_opacity(target,0,100,(duration || 500));return false;}
//efects
function j_opacity(id, opacStart, opacEnd, millisec) {var speed = Math.round(millisec / 100);	var timer = 0;if(opacStart > opacEnd){for(i = opacStart; i >= opacEnd; i--){setTimeout("j_c_o(" + i + ",'" + id + "')",(timer * speed));timer++;}} else if(opacStart < opacEnd){for(i = opacStart; i <= opacEnd; i++){setTimeout("j_c_o(" + i + ",'" + id + "')",(timer * speed));timer++;}}}
//change the opacity for different browsers
function j_c_o(opacity, id)
{var object = m(id).style;if(object){object.opacity = (opacity / 100);object.MozOpacity = (opacity / 100);object.KhtmlOpacity = (opacity / 100);object.filter = "alpha(opacity=" + opacity + ")";}}
function j_event(t, fn, o) {o = o || window; var e = t+Math.round(Math.random()*99999999);if ( o.attachEvent ) {o['e_click_'+e] = fn;
o[e] = function(){o['e_click_'+e]( window.event ); };o.attachEvent( 'on'+t, o[e] ); }else{o.addEventListener( t, fn, false );}}
function j_ajax_get(url,target,evil) {j_ajax('GET',url,target,evil) }
function j_ajax_post(url,target,evil) {j_ajax('POST',url,target,evil) }
function j_ajax(method,url,target,evil) 
{
payload = false
if (method != 'POST'){
payload = evil
}
if (window.XMLHttpRequest) {
req[target] = new XMLHttpRequest();

	if( method != 'POST'){
        req[target].onreadystatechange = function() {j_ajax_klaar(target,payload);};
	req[target].open(method, url, true);
	req[target].send(null);
	}
	else
	{
	req[target].open(method, url, true);
	//Send the proper header information along with the request
       req[target].onreadystatechange = function() {//Call a function when the state changes.
	if(req[target].readyState == 4 && req[target].status == 200) {
		j_ajax_klaar(target,payload);
	}
}
        
	req[target].send(evil);

	}

} 
else if (window.ActiveXObject) {req[target] = new ActiveXObject("Microsoft.XMLHTTP");
if (req[target]) {req[target].onreadystatechange = function() {
j_ajax_klaar(target,evil);};
req[target].open(method, url, true);
req[target].send();}
}
}
function j_ajax_klaar(target,evil){if (req[target].readyState === 4) {if (req[target].status === 200) {
ajax_results[target] = req[target].responseText;

if (evil){eval(ajax_results[target]);}
else if(target){
if (j_ie_hell<9){ //fuck ie
e= document.getElementById(target)
e.innerHTML=''
 var div = document.createElement('div');
div.innerHTML = ajax_results[target]
e.appendChild(div)
}
else
{m(target).innerHTML = ajax_results[target];}
} 
else {return ajax_results[target];}}}}

function escapeHTML(someText) {
  var div = document.createElement('div');
  div.innerHTML = someText;
 // div.appendChild(someText);
  return div.innerHTML;
}



function j_register(naam,waarde){if(waarde){cached_items[naam]=waarde;} else {return cached_items[naam] || null;}}
/*mouse*/
function j_mouse(e){var posx=0,posy = 0; if(!e){e = window.event;}if (e.pageX || e.pageY){ posx = e.pageX;posy = e.pageY; } else {if (e.clientX || e.clientY){  posx = e.clientX; posy = e.clientY;}}return [posx,posy]}