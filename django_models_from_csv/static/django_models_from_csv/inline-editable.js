(() => {
  const getCSRF = () => {
    return $("input[name='csrfmiddlewaretoken']")[0].value;
  };

  const doUpdate = (modelId, objectId, field, value) => {
    const url = "/db-config/object-updater/";
    const csrf = getCSRF();
    const body = {
      model: modelId,
      object: objectId,
      field: field,
      value: value,
      csrfmiddlewaretoken: csrf,
    };
    console.log("url:", url, "body:", body);
    $.post(url, body, function( data ) {
      // TODO: pop a success indicator (for a short period)
      console.log("Response data", data)
    }, "json");
  };

  const inlineChanged = (event) => {
    console.log("inlineChanged event:", event, "target:", event.target);
    event.preventDefault();
    event.stopPropagation();
    // get the row containing the editable widget
    // we're going to use this to get the content type ID
    // object ID and field name/value to send up to the
    // server side updater endpoint
    const thisRow = $(event.target).closest("tr");
    const name = $(event.target).attr("name")
    // TODO: get based on type
    const value = event.target.value;
    const objId = thisRow
      .find("input[type='checkbox'].action-select")[0]
      .value;
    const ctId = thisRow
      .closest("tr")
      .find("span.inline-editable")
      .attr("content_type_id");
    console.log(
      "content-type:", ctId,
      "object-id:", objId,
      "field-name:", name,
      "value:", value
    );
    doUpdate(ctId, objId, name, value);
  };

  // Don't allow events to propogate or do anything!
  // We want this to disable the automatic submit of
  // list view admin rows
  const disable = (event, el) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const setupSaving = (index, el) => {
    console.log("setupSaving", index, el);
    $(el).on("change", inlineChanged);
    $("#changelist-form").submit(disable);
  };

  const main = () => {
    $(".inline-editable").each(setupSaving);
  };

  $(document).ready(main);
})();
