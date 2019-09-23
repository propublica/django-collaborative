// Rivets.js
(() => {
  const dbgColumns = (d) => {
    d.columns.forEach((c, ix) => {
      console.log("Column", ix, c.ix, c.name, c.type);
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

  const sortCSS = "table#render-meta_columns tbody";

  const startSortable = () => {
    const options = {
      items: 'tr',
      forcePlaceholderSize: true,
    };

    const s = sortable(sortCSS, options);
    s[0].addEventListener('sortupdate', function(e) {
      console.warn("sortable update data");
      const start = e.detail.origin.index;
      const end = e.detail.destination.index;
      console.log("start", start, "end", end);
      //const dest = data.columns[end];
      //data.columns[end] = data.columns[start];
      //data.columns[start] = dest;
      data.swapitems(start, end);
      console.warn("sortupdate complete");
      dbgColumns(data);
    });

    console.warn("startSortable complete");
    dbgColumns(data);
  };

  let bound = null;
  const main = () => {
    bound = rivets.bind($("#render-meta_columns"), data);
    startSortable();
  };

  // add blank field, this is outside of the scope of the
  // bound rivets object so we attach it to the window
  window.COLLABaddField = (widgetSelector) => {
    console.warn("Adding field");
    const widget = $(widgetSelector);
    // re-enable the sortable to get the new field to work. we
    // need to start sorting *after* we mutate the columns list.
    sortable(sortCSS, "destroy");
    bound.unbind();
    data.columns.push({
      ix: data.columns.length,
      name: '',
      type: 'text',
      value: null,
      filterable: false,
      searchable: false,
    });
    bound = rivets.bind($("#render-meta_columns"), data);
    startSortable();
  };

  $(document).ready(main);
})();
