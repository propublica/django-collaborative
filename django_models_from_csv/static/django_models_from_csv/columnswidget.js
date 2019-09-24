// Rivets.js
(() => {
  const sortCSS = "table#render-meta_columns tbody";
  const dbgColumns = (d) => {
    d.columns.forEach((c, ix) => {
      console.log("Column", ix, c.ix, c.name||"[blank]", c.type);
    });
  };

  // TODO: update the textarea with the state of the columns
  const updateState = (d) => {
    console.info("updateState");
    dbgColumns(d);
  };

  // TODO: fetch columns data from API or injected onto window
  const data = {
    columns: [{
      ix: 0,
      name: 'status',
      type: 'choice',
      value: 'Available,Spam',
      filterable: true,
      searchable: true,
    },{
      ix: 1,
      name: 'assigned-to',
      type: 'short-text',
      value: 'option-3',
      filterable: true,
      searchable: true,
    },{
      ix: 2,
      name: 'test',
      type: 'text',
      value: null,
      filterable: true,
      searchable: true,
    }],
    destroy: (ev, scope) => {
      data.columns.splice(scope.index, 1);
    },
    onchange: (ev, scope) => {
      updateState(data);
    },
    swapitems: (a, b) => {
      console.log("a", a, "b", b);
      console.log("this", this);
    },
    addField: (ev, scope) => {
      console.log("Adding field");
      // re-enable the sortable to get the new field to work. we
      // need to start sorting *after* we mutate the columns list.
      //sortable(sortCSS, "destroy");
      data.columns = data.columns.concat([{
        ix: data.columns.length,
        name: '',
        type: 'text',
        value: null,
        filterable: false,
        searchable: false,
      }]);
      //startSortable();
      dbgColumns(data);
    },
  };

  const makeDefaultColumn = () => {
    return {
      name: '',
      type: 'text',
      value: null,
      filterable: false,
      searchable: false,
    };
  };

  const startSortable = () => {
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
        var movedItem = data.columns[ui.item.startPos];
        console.log("end", endPos, "start", startPos);
        console.log("moved item", movedItem);

        $(sortCSS).sortable("cancel");

        // Remove the view from its original location
        data.columns.splice(startPos, 1);

        // Add it to its new location
        data.columns.splice(endPos, 0, movedItem);

        // show the order of the model
        dbgColumns(data);
      },
    };

    $(sortCSS).sortable(options);
    dbgColumns(data);
  };

  const main = () => {
    rivets.bind($("#render-meta_columns"), data);
    rivets.bind($(".meta_columns .add-record"), data);
    startSortable();
  };

  $(document).ready(main);
})();
