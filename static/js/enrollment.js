let enrollmentFormState = {};

function saveFormState(form) {
  enrollmentFormState = {};

  new FormData(form).forEach((value, key) => {
    if (key in enrollmentFormState) {
      enrollmentFormState[key] = [].concat(enrollmentFormState[key], value);
    } else {
      enrollmentFormState[key] = value;
    }
  });

  form.querySelectorAll("input[type='checkbox']").forEach((input) => {
    enrollmentFormState[input.name] = input.checked;
  });
}

// Map each toggle checkbox to the wrapper holding its dependent fields.
const CONDITIONAL_FIELD_MAP = {
  has_allergy: "allergy-fields",
  has_medical_note: "medical-note-fields",
  has_custody_restriction: "custody-restriction-fields",
  create_emergency_contact: "emergency-contact-fields",
  emergency_is_authorized: "emergency-authorized-fields",
};

function applyConditionalField(form, checkboxName, targetId) {
  const checkbox = form.querySelector(`[name="${checkboxName}"]`);
  const target = form.querySelector(`#${targetId}`);
  if (!checkbox || !target) return;
  target.classList.toggle("d-none", !checkbox.checked);
}

function setupConditionalFields(form) {
  Object.entries(CONDITIONAL_FIELD_MAP).forEach(([checkboxName, targetId]) => {
    const checkbox = form.querySelector(`[name="${checkboxName}"]`);
    if (!checkbox) return;
    applyConditionalField(form, checkboxName, targetId);
    checkbox.addEventListener("change", () =>
      applyConditionalField(form, checkboxName, targetId)
    );
  });
}

function restoreFormState(form) {
  Object.entries(enrollmentFormState).forEach(([key, value]) => {
    form.querySelectorAll(`[name="${key}"]`).forEach((field) => {
      if (field.type === "checkbox") {
        field.checked = Boolean(value);
      } else if (field.type === "radio") {
        field.checked = field.value === value;
      } else {
        field.value = value;
      }
    });
  });
}

// Django stamps a hidden CSRF input via {% csrf_token %}; reuse its value so
// the fetch() POST survives CsrfViewMiddleware.
function getCsrfToken(form) {
  const tokenInput = form.querySelector("input[name='csrfmiddlewaretoken']");
  return tokenInput ? tokenInput.value : "";
}

function clearFieldErrors(form) {
  form
    .querySelectorAll(".is-invalid")
    .forEach((field) => field.classList.remove("is-invalid"));
  form
    .querySelectorAll(".enrollment-field-error")
    .forEach((feedback) => feedback.remove());
}

// Paint Django's field errors onto the matching inputs (Bootstrap 5 styling)
// and return any leftover message (non-field errors, or errors for fields not
// present in the DOM) for the caller to surface as a summary.
function renderFieldErrors(form, errors) {
  clearFieldErrors(form);
  if (!errors) return "";

  let summary = "";
  const appendSummary = (message) => {
    summary = summary ? `${summary} ${message}` : message;
  };

  Object.entries(errors).forEach(([fieldName, errorList]) => {
    const message = errorList
      .map((error) => (typeof error === "string" ? error : error.message))
      .join(" ");

    if (fieldName === "__all__") {
      appendSummary(message);
      return;
    }

    const fields = form.querySelectorAll(`[name="${fieldName}"]`);
    if (!fields.length) {
      appendSummary(message);
      return;
    }

    fields.forEach((field) => field.classList.add("is-invalid"));

    const anchor = fields[fields.length - 1];
    const feedback = document.createElement("div");
    feedback.className = "invalid-feedback d-block enrollment-field-error";
    feedback.textContent = message;
    anchor.insertAdjacentElement("afterend", feedback);
  });

  const firstInvalid = form.querySelector(".is-invalid");
  if (firstInvalid) {
    firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return summary;
}

function submitEnrollmentForm(form) {
  return fetch(form.action, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCsrfToken(form),
    },
    body: new FormData(form),
  })
    .then((response) =>
      response.json().then((data) => ({ ok: response.ok, data }))
    )
    .then(({ ok, data }) => {
      if (ok && data.success) {
        return data;
      }
      const summary = renderFieldErrors(form, data.errors);
      Swal.showValidationMessage(
        summary || "Please correct the highlighted fields and try again."
      );
      return false;
    })
    .catch(() => {
      Swal.showValidationMessage(
        "Something went wrong submitting the form. Please try again."
      );
      return false;
    });
}

function showEnrollmentModal() {
  const formHtml = document.getElementById("enrollment-form-template").innerHTML;

  Swal.fire({
    html: formHtml,
    width: "1521px",
    showCancelButton: true,
    confirmButtonText: "Create Enrollment",
    cancelButtonText: "Close Form",
    allowOutsideClick: false,
    allowEscapeKey: false,
    focusConfirm: false,

    didOpen: () => {
      const form = Swal.getPopup().querySelector("#enrollment-form");
      restoreFormState(form);
      setupConditionalFields(form);
    },

    // Save state here — popup DOM is still accessible
    willClose: () => {
      const form = Swal.getPopup().querySelector("#enrollment-form");
      if (form) saveFormState(form);
    },

    // Submit over AJAX. Returning the fetch promise makes SweetAlert show its
    // loading spinner; resolving to `false` keeps the modal open so inline
    // validation errors stay visible, while the success payload is handed back
    // through result.value.
    preConfirm: () => {
      const form = Swal.getPopup().querySelector("#enrollment-form");
      return submitEnrollmentForm(form);
    },
  }).then((result) => {
    if (result.isConfirmed && result.value && result.value.success) {
      enrollmentFormState = {};
      showSuccessModal(result.value.child_name, result.value.child_detail_url);
    } else if (result.dismiss === Swal.DismissReason.cancel) {
      showCloseConfirmation();
    }
  });
}

function showCloseConfirmation() {
  Swal.fire({
    title: "Close this form?",
    text: "Your entered data will stay available if you keep editing.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, close it",
    cancelButtonText: "No, keep editing",
  }).then((result) => {
    if (!result.isConfirmed) {
      showEnrollmentModal();
    } else {
      enrollmentFormState = {};
    }
  });
}

function showSuccessModal(name, childDetailURL) {
  Swal.fire({
    title: "Child Successfully Enrolled!",
    text: `You have successfully enrolled ${name}!`,
    icon: "success",
    showCancelButton: true,
    confirmButtonText: "See Details",
    cancelButtonText: "Close",
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = childDetailURL;
    }
  });
}

const openEnrollmentTrigger = document.getElementById("open-enrollment-modal");
if (openEnrollmentTrigger) {
  openEnrollmentTrigger.addEventListener("click", (event) => {
    event.preventDefault();
    showEnrollmentModal();
  });
}
