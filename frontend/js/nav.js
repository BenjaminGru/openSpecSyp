// Marks the navigation entry for the current page.
// Each page sets <body data-page="...">, and each nav link has a matching
// data-page value, so the active entry is unambiguous even for "/".
(function () {
  "use strict";

  const current = document.body.dataset.page;
  const links = document.querySelectorAll(".site-nav a[data-page]");

  links.forEach(function (link) {
    const isCurrent = link.dataset.page === current;
    link.classList.toggle("active", isCurrent);
    if (isCurrent) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
})();
