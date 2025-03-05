const slider = document.querySelector(".slider2");
const images = document.querySelectorAll(".slider img");
const prevBtn = document.querySelector(".prev");
const nextBtn = document.querySelector(".next");

let currentIndex = 0;
const totalSlides = images.length;

function updateSlide() {
    if(currentIndex.length<0){
    slider.style.transform = `translateX(-${currentIndex * 100}%)`;}
    
}

function nextSlide() {
    currentIndex = (currentIndex + 1) % totalSlides;
    updateSlide();
}

function prevSlide() {
    currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
    updateSlide();
}

// Auto slide every 3 seconds
let slideInterval = setInterval(nextSlide, 3000);

// Event listeners for buttons
nextBtn.addEventListener("click", () => {
    nextSlide();
    resetInterval();
});

prevBtn.addEventListener("click", () => {
    prevSlide();
    resetInterval();
});

// Reset auto-slide timer when manually changing slides
function resetInterval() {
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 3000);
}