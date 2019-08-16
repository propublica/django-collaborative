(() => {
  /**
   * Pop the success/failure bar at the top of the admin along
   * with a specified message.
   *
   * success (Boolean) -- False means failure (also styles accordingly)
   * message (String) -- Message to be displayed to the user inside the box.
   */
  const notify = (success, message) => {
    const block = $("#inline-editable-notifier");
    block.addClass(success ? "success" : "failure");
    block.text(message);
    block.show();

    const duration = success ? 2000 : 5000;
    $("#inline-editable-notifier").fadeOut(duration, () => {
      block.removeClass("success");
      block.hide();
    })
  };

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
    $.post(url, body, (data, status, xhr) => {
      console.log("Response data:", data, "status:", status, "xhr:", xhr);
      notify(xhr.status === 200, data.message);
    }, "json");
  };

  const inlineChanged = (event) => {
    window.E = event;
    window.T = event.target;
    console.log("inlineChanged event:", event, "target:", event.target);
    event.preventDefault();
    event.stopPropagation();

    // get the row containing the editable widget
    // we're going to use this to get the content type ID
    // object ID and field name/value to send up to the
    // server side updater endpoint
    const thisRow = $(event.target).closest("tr");
    window.R = thisRow;

    let name = $(event.target).attr("name");
    // try for tag autocomplete field
    if (!name && $(event.target).hasClass("select2-search__field")) {
      name = thisRow.find(
        "span[data-autocomplete-light-function='select2']"
      ).attr("name");
    }
    const value = event.target.value;

    // content-type model ID
    const ctId = thisRow
      .closest("tr")
      .find("span.inline-editable")
      .attr("content_type_id");
    // object ID
    const objId = thisRow
      .find("input[type='checkbox'].action-select")[0]
      .value;

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
    $(el).on("change", inlineChanged);
    $("#changelist-form").submit(disable);
  };

  const getTags = (el) => {
    const tags = [];
    $(el)
      .find(".select2-selection__choice")
      .each((i, e) => {
        console.log("getting tag", e.title);
        tags.push(e.title);
      });
    return tags;
  };

  const setTags = (el, tagList) => {
    $(el)
      .find(".select2-selection__choice")
      .each((i, e) => {
        if (tagList.indexOf(e.title) === -1) {
          console.log("setting tag", e.title);
          tagList.push(e.title);
        }
      });
  };

  const updateTags = (originalTags, newTags) => {
    console.log("originalTags", originalTags, "newTags", newTags);
    const updatedTags = [];
    // we removed a tag
    if (originalTags.length < newTags.length) {
      console.log("ADDED TAG");
    }
    // we added a tag
    else if (originalTags.length > newTags.length) {
      console.log("REMOVED TAG");
    }
  };

  const tagChanged = (originalTags, el, event) => {
    // We need the timeout due to an inability of normal onchange event
    // to work with the select2 library. I've identified one reason why
    // javascript developers tend to go insane with time.
    setTimeout(() => {
      console.log("--------------------");
      console.log("originalTags", originalTags);
      const newTags = getTags(el);
      console.log("newTags", newTags);
      updateTags(originalTags, newTags);
    }, 500);
  };

  const setupTagsSaving = (index, el) => {
    const originalTags = [];
    setTags(el, originalTags);

    console.log("--------------------");
    console.log("setupTagsSaving tags:", originalTags);
    //window.ELL = el;

    const thisRowColumn = $(el).closest("td");
    const id = `${Date.now()}.${Math.random()}`.replace(/\./g, "");
    console.log("id", id);
    $(el).attr("id", id);
    //$(el.parentElement).on("change", tagChanged.bind(this, originalTags, el));
    $(el.parentElement).on("select2:select", () => {
      alert("HELLO");
    });
    $(el.parentElement).on("select2:unselect", () => {
      alert("BYE");
    });
  };

  const main = () => {
    $(".inline-editable").each(setupSaving);
    const tagEls = $(".inline-editable-tags").find(".select2");
    tagEls.each(setupTagsSaving);
  };

  $(document).ready(main);
})();
