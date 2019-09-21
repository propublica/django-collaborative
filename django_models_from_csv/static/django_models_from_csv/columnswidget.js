// Rivets.js
(() => {
  const data = {
    columns: [{
      ix: 0,
      name: 'status',
      type: 'choice',
      value: 'Available',
      filterable: true,
      searchable: true,
    },{
      ix: 1,
      name: 'assigned-to',
      type: 'short-text',
      value: 'option-3',
      filterable: true,
      searchable: true,
    }]
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

  const main = () => {
    rivets.bind($("#render-meta_columns"), data);
  };

  window.addField = (widgetSelector) => {
    const widget = $(widgetSelector);
    data.columns.push(makeDefaultColumn());
  };

  $(document).ready(main);
})();
