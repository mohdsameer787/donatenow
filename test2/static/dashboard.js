
function toggle(){
    let panal=document.querySelector(".panale")
    let btn=document.querySelector(".slider-btn")

    if(panal.classList=="new1"){
        panal.classList.toggle("logodiv2");
        panal.classList.toggle("panale");
        btn.classList.toggle("newbtn");
    }
    
    
    
    panal.classList.toggle("new1");
    
}  
function toggle2(){
    let panal=document.querySelector(".panale")
    

    if(panal.classList=="panale"){
        panal.classList.toggle("new1");
    }
    
    
    
    
}  

