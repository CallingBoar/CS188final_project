// This file should be placed in static/js, and should be called auth.js
// base.html includes it on every page, after Bootstrap's JavaScript.

// Characters enclosed in / / are regular expressions.
// ^ means start of the string, $ means end of the string.
// [a-zA-Z0-9] means any alphanumeric character.
// {1,20} means between 1 and 20 of them.
// So this matches any string made of 1 to 20 alphanumeric characters.
const USERNAME_PATTERN = /^[a-zA-Z0-9]{1,20}$/;

// \x21-\x7E is the range of ASCII characters from ! to ~ (so no spaces).
// You can find the full ASCII table at https://ss64.com/ascii.html
// {8,} means at least 8 of them.
const PASSWORD_PATTERN = /^[\x21-\x7E]{8,}$/;

// Mark an input as valid: Bootstrap draws it with a green border.
function setValid(input) {
	input.classList.remove("is-invalid");
	input.classList.add("is-valid");
}

// Mark an input as invalid: Bootstrap draws it with a red border and shows the
// .invalid-feedback element right after it.
function setError(input, message) {
	input.classList.add("is-invalid");
	input.classList.remove("is-valid");
	const feedback = input.parentElement.querySelector(".invalid-feedback");
	if (feedback) {
		feedback.textContent = message;
	}
}

// Each validate function takes the id of an input, marks it valid or invalid,
// and returns true if it was valid.
function validatePassword(id) {
	const password = document.getElementById(id);
	// .test() checks whether the text matches the regular expression.
	// .value is the text the user typed into the input.
	if (!PASSWORD_PATTERN.test(password.value)) {
		setError(password, "Password must be at least 8 characters with no spaces.");
		return false;
	}
	setValid(password);
	return true;
}

function validateUsername(id) {
	const username = document.getElementById(id);
	if (!USERNAME_PATTERN.test(username.value)) {
		setError(username, "Username must be alphanumeric and at most 20 characters.");
		return false;
	}
	setValid(username);
	return true;
}

function validateDisplayName(id) {
	const displayName = document.getElementById(id);
	// .trim() removes spaces from both ends, so "   " counts as empty.
	if (displayName.value.trim() === "") {
		setError(displayName, "Display name cannot be empty.");
		return false;
	}
	setValid(displayName);
	return true;
}

// Close a Bootstrap modal from JavaScript. `bootstrap` is a global object that
// Bootstrap's script creates, which is why base.html loads this file after it.
function hideModal(id) {
	const modal = bootstrap.Modal.getInstance(document.getElementById(id));
	// ?. means "only call hide() if getInstance found something".
	modal?.hide();
}

// Send `data` as JSON in a POST request to `url`.
// Returns the response and the parsed JSON body, or null if the server
// couldn't be reached or didn't send back JSON.
//
// `async` lets us use `await`, which pauses this function until the network
// request finishes, without freezing the rest of the page while it waits.
async function postJson(url, data) {
	try {
		const response = await fetch(url, {
			method: "POST", // We are sending data, so we use POST
			headers: { "Content-Type": "application/json" }, // Tell the server the body is JSON
			body: JSON.stringify(data), // Turn the JavaScript object into a JSON string
		});
		const result = await response.json();
		return { response, result };
	} catch {
		// fetch() throws if the server can't be reached, and .json() throws if the
		// server sent back something that isn't JSON (like an HTML error page).
		return null;
	}
}

// Runs when the register form is submitted.
async function submitRegisterForm(event) {
	// Without this, the browser would submit the form itself and reload the page,
	// and our code below would never get to send the request.
	event.preventDefault();

	// We want every invalid field to light up red at once, not just the first one.
	// That's why each validate call goes on the LEFT of the &&. JavaScript stops
	// evaluating && as soon as it knows the answer (short-circuit evaluation), so
	// if we wrote `isValid && validateUsername(...)`, validateUsername would never
	// run once the password had already failed.
	let isValid = validatePassword("registerPassword");
	isValid = validateUsername("registerUsername") && isValid;
	isValid = validateDisplayName("registerDisplayName") && isValid;
	if (!isValid) {
		return;
	}

	// The keys here must match what the server reads in Register.post().
	const formData = {
		username: document.getElementById("registerUsername").value,
		password: document.getElementById("registerPassword").value,
		displayName: document.getElementById("registerDisplayName").value,
	};

	const reply = await postJson("/register", formData);
	if (reply === null) {
		alert("Could not reach the server. Please try again.");
		return;
	}

	// response.ok is true for status codes 200-299 (we send 201 on success).
	if (!reply.response.ok) {
		alert("Registration failed: " + reply.result.message);
		return;
	}

	alert("Registration successful! Welcome, " + reply.result.displayName);
	hideModal("registerModal");
}


async function submitLoginForm(event) {
	event.preventDefault();
	const formData = {
		username: document.getElementById("loginUsername").value,
		password: document.getElementById("loginPassword").value,
	};

	const reply = await postJson("/login", formData);
	if (reply === null) {
		alert("Could not reach the server. Please try again.");
		return;
	}

	if (!reply.response.ok) {
		alert("Login failed: " + reply.result.message);
		return;
	}
	window.location.assign("account");

	//alert(reply.result.message);
	//hideModal("loginModal");
}

// Runs when the logout button is clicked.
async function logout() {
	const reply = await postJson("/logout", {});
	if (reply === null || !reply.response.ok) {
		alert("Logout failed. Please try again.");
		return;
	}
	// Go back to the home page. This loads a fresh page, so the navbar is
	// rendered again without the session cookie.
	window.location.href = "/";
}

async function fullLogout() {
	const reply = await postJson("/full-logout", {});
	if (reply === null || !reply.response.ok) {
		alert("Full logout failed. Please try again.");
		return;
	}
	// Go back to the home page. This loads a fresh page, so the navbar is
	// rendered again without the session cookie.
	window.location.href = "/";
}

// Remove the green/red validation styling from an input once the user starts
// typing in it again.
function clearValidation(event) {
	event.target.classList.remove("is-invalid", "is-valid");
}

// Empty out every form inside a modal after the modal closes, so that the next
// time it opens it starts fresh.
//
// Bootstrap fires a "hidden.bs.modal" event on a modal once it has finished
// closing. Like every event listener, this function receives the event object,
// and event.target is the modal that just closed.
function resetModalForms(event) {
	for (const form of event.target.querySelectorAll("form")) {
		// reset() puts every input in the form back to its starting value.
		form.reset();
		// reset() doesn't know about Bootstrap's classes, so we remove them ourselves.
		for (const input of form.querySelectorAll(".is-valid, .is-invalid")) {
			input.classList.remove("is-valid", "is-invalid");
		}
	}
}

// Connect our functions to the elements on the page.
function attachEventListeners() {
	// ?. means "only call addEventListener if the element exists". Every page
	// includes this script, but a page might not have every form on it.
	document.getElementById("registerForm")?.addEventListener("submit", submitRegisterForm);
	document.getElementById("loginForm")?.addEventListener("submit", submitLoginForm);
	document.getElementById("logoutButton")?.addEventListener("click", logout);
	document.getElementById("fullLogout")?.addEventListener("click", fullLogout);

	for (const input of document.querySelectorAll("input")) {
		input.addEventListener("input", clearValidation);
	}

	// One listener per modal, so any modal we add later gets this for free.
	for (const modal of document.querySelectorAll(".modal")) {
		modal.addEventListener("hidden.bs.modal", resetModalForms);
	}
}

// Run attachEventListeners once the page's HTML has loaded. If it has already
// loaded by the time this script runs, run it right away. Otherwise, wait for
// the DOMContentLoaded event.
function onReady(callback) {
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", callback);
	} else {
		callback();
	}
}

// The only top-level code in this file. Everything else happens in functions.
onReady(attachEventListeners);
