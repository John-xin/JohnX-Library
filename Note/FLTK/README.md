# FLTK-Study-Record

Example 1: // use a button and response when clicking the button
#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Button.H>
using namespace std;

//jw: response func to button click event
void but_cb( Fl_Widget* o, void*  ) {
   Fl_Button* b=(Fl_Button*)o; //jw: parent type downcast to child type
   b->label("Good job"); //jw: label() and value() func redraw automatically
   b->resize(10,150,140,30); //redraw needed
   b->redraw();
}
//jw: discussion:
//Fl_Widget is parent class
//Fl_Button is child class
//Using parent type to define/receive child object is ok

//--------------------------------------------  
int main() {
    Fl_Window win( 300,200,"Testing" ); //jw: win_len, win_width, win_name_label
    win.begin();//jw: optional
       Fl_Button but( 10, 150, 70, 30, "Click me" );//jw: x,y,  l, w, label - origin at left up corner
    win.end();
    but.callback( but_cb ); //jw: button's click event callback - call the response func 
    win.show();
    return Fl::run();
}
//jw: discussion: callback mechanism
// button derived from widget
// widget has member-function callback(Fl_Callback*, void* = 0) to receive the cb_func referene and userdata, 
// then pass itself reference and userdata to cb_func's parameter
// but.callback(but_cb_func)
// but_cb_func(Fl_Widget* o, void* ) 
