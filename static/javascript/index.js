const r_value=document.querySelector("#rvalue");
const star=document.querySelector('.star-rating').children;
for(let i=0; i<star.length; i++){
star[i].addEventListener('mouseover',function(){
    for (let j=0;j<star.length;j++){
        star[j].classList.remove("fa-star");
        star[j].classList.add("fa-star-o");
    }

    for (let j=0;j<=i;j++){
    star[j].classList.remove("fa-star-o");
    star[j].classList.add("fa-star");
}
})
star[i].addEventListener('click',function(){
   r_value.innerHTML=i+1;
})
}
