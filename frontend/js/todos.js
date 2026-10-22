// ToDo list frontend. All state lives in the backend; after every change the
// list is re-fetched so the page always mirrors the database.
(function () {
  "use strict";

  const API_URL = "/api/todos";

  const elements = {
    form: document.getElementById("create-form"),
    title: document.getElementById("new-title"),
    description: document.getElementById("new-description"),
    submit: document.querySelector("#create-form button[type='submit']"),
    list: document.getElementById("todo-list"),
    empty: document.getElementById("empty-state"),
    loading: document.getElementById("loading"),
    error: document.getElementById("error-banner"),
  };

  function showError(message) {
    elements.error.textContent = message;
    elements.error.hidden = false;
  }

  function clearError() {
    elements.error.textContent = "";
    elements.error.hidden = true;
  }

  function describeFailure(data, status) {
    if (data && typeof data.detail === "string") {
      return data.detail;
    }
    if (data && Array.isArray(data.detail) && data.detail.length > 0) {
      return data.detail.map(function (entry) {
        return entry.msg || "Invalid value";
      }).join("; ");
    }
    return "Request failed (HTTP " + status + ").";
  }

  async function request(path, options) {
    const settings = options || {};
    const init = { method: settings.method || "GET" };
    if (settings.body !== undefined) {
      init.headers = { "Content-Type": "application/json" };
      init.body = JSON.stringify(settings.body);
    }

    let response;
    try {
      response = await fetch(path, init);
    } catch (error) {
      throw new Error("Could not reach the server. Check that the backend is running.");
    }

    if (response.status === 204) {
      return null;
    }

    let data = null;
    try {
      data = await response.json();
    } catch (error) {
      data = null;
    }

    if (!response.ok) {
      throw new Error(describeFailure(data, response.status));
    }
    return data;
  }

  function formatDate(value) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
  }

  function makeButton(label, styles, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "button" + (styles ? " " + styles : "");
    button.textContent = label;
    button.addEventListener("click", onClick);
    return button;
  }

  function makeField(labelText, control) {
    const field = document.createElement("div");
    field.className = "field";
    const label = document.createElement("label");
    label.textContent = labelText;
    label.htmlFor = control.id;
    field.append(label, control);
    return field;
  }

  function render(todos) {
    elements.list.replaceChildren.apply(elements.list, todos.map(createItem));
    elements.empty.hidden = todos.length > 0;
  }

  function createItem(todo) {
    const item = document.createElement("li");
    item.className = "todo-item" + (todo.completed ? " completed" : "");
    item.dataset.id = String(todo.id);

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.completed;
    checkbox.setAttribute(
      "aria-label",
      'Mark "' + todo.title + '" as ' +
        (todo.completed ? "not completed" : "completed")
    );
    checkbox.addEventListener("change", function () {
      toggleCompleted(todo, checkbox);
    });

    const main = document.createElement("div");
    main.className = "todo-main";

    const title = document.createElement("p");
    title.className = "todo-title";
    title.textContent = todo.title;

    const description = document.createElement("p");
    description.className = "todo-description";
    description.textContent = todo.description || "No description";

    const meta = document.createElement("p");
    meta.className = "todo-meta";
    meta.textContent = "Created " + formatDate(todo.created_at);

    main.append(title, description, meta);

    const actions = document.createElement("div");
    actions.className = "todo-actions";
    actions.append(
      makeButton("Edit", "secondary", function () {
        startEdit(item, todo);
      }),
      makeButton("Delete", "danger", function () {
        deleteTodo(todo);
      })
    );

    item.append(checkbox, main, actions);
    return item;
  }

  async function loadTodos() {
    elements.loading.hidden = false;
    try {
      const todos = await request(API_URL);
      render(todos);
      clearError();
    } catch (error) {
      showError(error.message);
    } finally {
      elements.loading.hidden = true;
    }
  }

  async function toggleCompleted(todo, checkbox) {
    checkbox.disabled = true;
    try {
      await request(API_URL + "/" + todo.id, {
        method: "PATCH",
        body: { completed: checkbox.checked },
      });
      clearError();
      await loadTodos();
    } catch (error) {
      showError(error.message);
      checkbox.checked = !checkbox.checked;
      checkbox.disabled = false;
    }
  }

  async function deleteTodo(todo) {
    if (!window.confirm("Delete \"" + todo.title + "\"? This cannot be undone.")) {
      return;
    }
    try {
      await request(API_URL + "/" + todo.id, { method: "DELETE" });
      clearError();
      await loadTodos();
    } catch (error) {
      showError(error.message);
    }
  }

  function startEdit(item, todo) {
    const form = document.createElement("form");
    form.className = "todo-edit-form";

    const titleInput = document.createElement("input");
    titleInput.type = "text";
    titleInput.id = "edit-title-" + todo.id;
    titleInput.maxLength = 200;
    titleInput.required = true;
    titleInput.value = todo.title;

    const descriptionInput = document.createElement("textarea");
    descriptionInput.id = "edit-description-" + todo.id;
    descriptionInput.rows = 2;
    descriptionInput.maxLength = 2000;
    descriptionInput.value = todo.description;

    const actions = document.createElement("div");
    actions.className = "actions";

    const save = document.createElement("button");
    save.type = "submit";
    save.className = "button";
    save.textContent = "Save";

    const cancel = makeButton("Cancel", "secondary", function () {
      loadTodos();
    });

    actions.append(save, cancel);
    form.append(
      makeField("Title", titleInput),
      makeField("Description", descriptionInput),
      actions
    );

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      save.disabled = true;
      try {
        await request(API_URL + "/" + todo.id, {
          method: "PATCH",
          body: {
            title: titleInput.value,
            description: descriptionInput.value,
          },
        });
        clearError();
        await loadTodos();
      } catch (error) {
        showError(error.message);
        save.disabled = false;
      }
    });

    item.replaceChildren(form);
    titleInput.focus();
  }

  elements.form.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (!elements.title.value.trim()) {
      showError("Please enter a title.");
      elements.title.focus();
      return;
    }

    elements.submit.disabled = true;
    try {
      await request(API_URL, {
        method: "POST",
        body: {
          title: elements.title.value,
          description: elements.description.value,
        },
      });
      elements.form.reset();
      clearError();
      await loadTodos();
    } catch (error) {
      showError(error.message);
    } finally {
      elements.submit.disabled = false;
    }
  });

  loadTodos();
})();
