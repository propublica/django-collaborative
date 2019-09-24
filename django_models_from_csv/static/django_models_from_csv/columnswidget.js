// Rivets.js
(() => {
  /**
   * A generic widget handler that accepts a widget name
   * (a unique class and ID name, identifying a specific meta
   * widget container) and handles sorting, input updates and
   * managing the string JSON represenatation of data for
   * pushing via POST.
   */
  class WidgetHandler {
    constructor(widgetName) {
      this.widgetName = widgetName;
      this.sortCSS = `table#render-${widgetName} tbody`;

      // TODO: fetch columns data from API or injected onto window
      /*
      const columns = [{
        name: 'status',
        type: 'choice',
        value: 'Available,Spam',
        filterable: true,
        searchable: true,
      },{
        name: 'assigned-to',
        type: 'short-text',
        value: 'option-3',
        filterable: true,
        searchable: true,
      },{
        name: 'test',
        type: 'text',
        value: null,
        filterable: true,
        searchable: true,
      }];
      */

      this.data = {
        columns: this.getInitialColumns(),
        // type checker for rv-if on field options
        istype: (value, criteria) => {
          console.log("value", value, "criteria", criteria);
          return value === criteria;
        },
        // remove a field
        destroy: (ev, scope) => {
          this.data.columns.splice(scope.index, 1);
        },
        // if any selector/input is changed, this is called
        onchange: (ev, scope) => {
          this.updateState(this.data);
        },
        // add a new, blank field to the list
        addField: (ev, scope) => {
          console.log("Adding field");
          // re-enable the sortable to get the new field to work. we
          // need to start sorting *after* we mutate the columns list.
          //sortable(sortCSS, "destroy");
          this.data.columns = this.data.columns.concat([{
            name: '',
            type: 'text',
            value: null,
            filterable: false,
            searchable: false,
          }]);
          //startSortable();
          this.updateState(this.data);
          this.dbgColumns(this.data);
        },
      };
      // TODO: call this constructor once document is ready
      //$(document).ready(this.main);
      // bind our main list to the table
      this.tableBound = rivets.bind($(`#render-${this.widgetName}`), this.data);
      // and bind our add button, which is outside the scope of the table
      this.addBound = rivets.bind($(`.${this.widgetName} .add-record`), this.data);
      this.startSortable();

    }

    getInitialColumns() {
      const textArea = $(`#json-${this.widgetName}`);
      const jsonStr = textArea.val();
      return JSON.parse(jsonStr);
    }

    dbgColumns(d) {
      d.columns.forEach((c, ix) => {
        console.log("Column", ix, c.name||"[blank]", c.type);
      });
    }

    updateState(d) {
      console.info("updateState", d.columns);
      const jsonStr = JSON.stringify(d.columns, null, 2);
      const textArea = $(`#json-${this.widgetName}`);
      console.log("textArea", textArea);
      console.log("jsonStr", jsonStr);
      textArea.val(jsonStr);
    }

    makeDefaultColumn() {
      return {
        name: '',
        type: 'text',
        value: null,
        filterable: false,
        searchable: false,
      };
    }

    startSortable() {
      const options = {
        items: 'tr',
        forcePlaceholderSize: true,
        start: (event, ui) => {
          console.log("sort started");
          ui.item.startPos = ui.item.index();
          console.log("start position", ui.item.startPos);
        },
        stop: (e, ui) => {
          console.log("sort stopped");
          var endPos    = ui.item.index();
          var startPos  = ui.item.startPos;
          var movedItem = this.data.columns[ui.item.startPos];
          console.log("end", endPos, "start", startPos);
          console.log("moved item", movedItem);

          $(this.sortCSS).sortable("cancel");

          // Remove the view from its original location
          this.data.columns.splice(startPos, 1);

          // Add it to its new location
          this.data.columns.splice(endPos, 0, movedItem);

          // show the order of the model
          this.dbgColumns(this.data);
        },
      };

      $(this.sortCSS).sortable(options);
      this.dbgColumns(this.data);
    }
  }

  const main = () => {
    const metaHandler = new WidgetHandler("meta_columns");
    const contactMetaHandler = new WidgetHandler("contactmeta_columns");
  };

  $(document).ready(main);
})();
