(function($) {
  'use strict';

  function updateJSON(widget, event) {
    let columnsJSON = JSON.parse($("textarea", widget).val());
    let i = 0;
    $(".column-selector", widget).each((_, tr) => {
      const columnDef = {};
      $(".option", tr).each((_, td) => {
        const input = $("input", td);
        if (input) {
          const name = input.attr("name");
          const val = input.val();
          columnsJSON[i][name] = val;
        }
        const select = $("select", td);
        if (select) {
          const name = select.attr("name");
          const val = select.val();
          columnsJSON[i][name] = val;
        }
      })
      i++;
    })
    const jsonStr = JSON.stringify(columnsJSON, null, 2);
    $("textarea", widget).val(jsonStr);
  }

  function watchChange(widget) {
    const inputs = $("input", widget);
    inputs.each((_, input) => {
      $(input).on("keyup change", updateJSON.bind(this, widget));
    });
    const selects = $("select", widget);
    selects.each((_, sel) => {
      $(sel).on("keyup change", updateJSON.bind(this, widget));
    });
  }

  function main() {
    const widgets = $(".columns-widget");
    widgets.each((_, widget) => {
      watchChange(widget);
    });
  }

  $(document).ready(main);
})(django.jQuery);

