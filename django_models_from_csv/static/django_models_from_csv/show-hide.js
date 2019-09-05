/**
 * Toggle displaying the dropdowns. Keyed based on
 * the class name, triggered by H3 click.
 */
function showHide(cls) {
  var hide = "display: none;";
  if (!cls) return;
  var block = document.querySelector(`${cls}-body`);
  if (block.getAttribute("style") === hide) {
    document.querySelectorAll(`${cls}-body`).forEach((i) => {
      i.setAttribute("style", "");
    });
    document.querySelector(`${cls} .icon`).innerText = "➖";
    document.querySelectorAll(`${cls}-body input`).forEach((i) => {
      i.value = "";
    });
  } else {
    document.querySelectorAll(`${cls}-body`).forEach((i) => {
      i.setAttribute("style", hide);
    });
    document.querySelector(`${cls} .icon`).innerText = "➕";
    document.querySelectorAll(`${cls}-body input`).forEach((i) => {
      i.value = "";
    });
  }
}

function initShowHide() {
  // hide the menus secondarily so the instruction hiding
  // doesn't pop the Sheets/CSV menu
  const hideables = document.querySelectorAll(".show-hide");
  hideables.forEach((d) => {
    let found = false;
    d.querySelectorAll("input").forEach((i) => {
      console.log("i", i);
      if (i.value && i.type != "checkbox" && i.type != "hidden") {
        found = true;
      }
    });
    console.log("found?", found);
    if (!found) {
      d.setAttribute("style", "display: none;");
    }
  });
}
window.COLLAB_initShowHide = initShowHide;
