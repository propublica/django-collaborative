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
      this.nRecordsCSS = "#n_records";

      const initialColumns = this.getInitialColumns();
      console.log("initialColumns", initialColumns);

      const originalNames = initialColumns.map(c => c.name);
      console.log("originalNames", originalNames);

      const haveRecs = $(this.nRecordsCSS).val() !== "0";
      console.log("haveRecs", haveRecs);

      this.data = {
        haveRecs: haveRecs,
        // don't allow users to change the original fields. they have
        // to delete them and create them as a different type/name. this
        // is simply a way to ease the migrations on the backend
        isOriginalColumn: (name) => {
          return haveRecs && (originalNames.indexOf(name) !== -1);
        },
        columns: initialColumns,
        // type checker for rv-if on field options
        istype: (value, criteria) => {
          return value === criteria;
        },
        /**
         * This is a critical part. We don't ever want to show
         * certain types of fields, even though we need them
         * to exist inside of our data model, for POSTing up
         * to the backend that actually creates the model.
         */
        ishiddentype: (modeltype) => {
          const hide = modeltype === "tagging" || modeltype === "foreignkey";
          return hide;
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

      // setup the choice field formatter (for read and write)
      rivets.formatters.choices = {
        read: function(choices) {
          console.log("formatter:read choices", choices);
          if (!choices) {
            return "";
          }
          return choices.map(c => c[1]).join(", ");
        },
        publish: function(choices) {
          console.log("formatter:publish choices", choices)
          // This mostly follows the slugification of the django
          // slugify method in django.utils.text:slugify and the
          // small modifications introduced in our own backend version
          // here: django_models_from_csv/utils/common.py:slugify
          return choices.split(/,\s*/).map(c => {
            const label = c.trim().replace(/"+/, "");
            const slug = label.toLowerCase()
              .replace(/[^\w\s-]+/, "")
              .replace(/[-\s]+/, "-");
            return [slug, label];
          });
        }
      };

      // bind our main list to the table
      this.tableBound = rivets.bind($(this.sortCSS), this.data);
      // and bind our add button, which is outside the scope of the table
      this.addBound = rivets.bind($(`.${this.widgetName} .add-record`), this.data);
      this.startSortable();
    }

    /**
     * Get the initial user-editable columns from the DOM, and
     * also combine the hidden fields with the editable in the
     * POST-receiving textarea (JSON string). This also gets
     * updated on change. The result of this is that the editable
     * fields will only show up in the columns editor, but all fields
     * will be included in the final POST data.
     */
    getInitialColumns() {
      const textArea = $(`#json-${this.widgetName}`);
      const editableColumns = JSON.parse(textArea.val());
      const hiddenTextArea = $(`#hidden-${this.widgetName}`);
      const hiddenCols = JSON.parse(hiddenTextArea.val());
      const columns = editableColumns.concat(hiddenCols);
      const jsonStr = JSON.stringify(columns, null, 2);
      textArea.val(jsonStr);
      return editableColumns;
    }

    dbgColumns(d) {
      d.columns.forEach((c, ix) => {
        console.log("Column", ix, c.name||"[blank]", c.type);
      });
    }

    /**
     * The user has changed a value for some (visible) field.
     * We take the newly updated data, append the hidden data
     * and apply it to the textarea for POST to the backend.
     * This, in conjunction with getInitialColumns, ensures that
     * all column data will be pushed up to the backend once
     * editing is complete.
     */
    updateState(d) {
      const hiddenTextArea = $(`#hidden-${this.widgetName}`);
      const hiddenCols = JSON.parse(hiddenTextArea.val());
      const columns = d.columns.concat(hiddenCols);
      // TODO: do slugify here?
      console.log("columns", columns);
      const jsonStr = JSON.stringify(columns, null, 2);
      $(`#json-${this.widgetName}`).val(jsonStr);
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

  /**
   * Main entry point for initializing meta widget UI handlers.
   * If we ever add another related field, this has to get
   * modified for the new meta widget.
   */
  const main = () => {
    const metaHandler = new WidgetHandler("meta_columns");
    const contactMetaHandler = new WidgetHandler("contactmeta_columns");
  };

  $(document).ready(main);
})();
