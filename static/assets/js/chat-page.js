/**=====================
     Custom tab toggle 
==========================**/

var subscriptionBtn = document.getElementById("subscriptionBtn");
subscriptionBtn.addEventListener("click", function () {
    var divs = document.querySelector("[data-bs-target='#subscription']");
    if (divs) {
        divs.click();
    }
});


/**===========================
     li active & change content
==========================**/
var parentElement = document.getElementById("innerLink");
var listItems = parentElement.getElementsByTagName("li");

for (var i = 0; i < listItems.length; i++) {
    listItems[i].addEventListener("click", function (event) {
        var siblings = this.parentNode.children;
        for (var j = 0; j < siblings.length; j++) {
            siblings[j].classList.remove("active");
        }

        this.classList.add("active");
        // change content
        const attributeValue = event.target.getAttribute('data-title');
        targetDiv.textContent = attributeValue;
    });
}


