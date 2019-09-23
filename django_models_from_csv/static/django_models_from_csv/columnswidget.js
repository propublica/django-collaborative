// Rivets.js
(() => {
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
      console.log("onchange ev", ev, "scope", scope);
      // TODO: update the textarea with the state of the columns
    },
    ondrag: (ev, scope) => {
      console.log("ondrag ev", ev, "scope", scope);
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
    const sortCSS = "table#render-meta_columns tbody";
    const options = {
      items: 'tr',
      forcePlaceholderSize: true,
    };
    const s = sortable(sortCSS, options);
    s[0].addEventListener('sortupdate', function(e) {
      console.log("sortable update", e);
    });
  };

  const main = () => {
    rivets.bind($("#render-meta_columns"), data);
    startSortable();
  };

  // add blank field, this is outside of the scope of the
  // bound rivets object so we attach it to the window
  window.COLLABaddField = (widgetSelector) => {
    const widget = $(widgetSelector);
    data.columns.push(makeDefaultColumn());
  };

  $(document).ready(main);
})();
