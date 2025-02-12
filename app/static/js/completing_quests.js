function submitAnswer(event) {
	event.preventDefault();
	
	const questId = window.location.pathname.split('/').pop();
	const answer = document.getElementById('answer').value;
	const resultDiv = document.getElementById('result');

	fetch(`/quest/${questId}/submit`, {
			method: 'POST',
			headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: `answer=${encodeURIComponent(answer)}`
	})
	.then(response => response.text())
	.then(data => {
			if (data === "Correct! Points added to your profile.") {
					resultDiv.innerHTML = `<div class="alert alert-success">${data}</div>`;
					setTimeout(() => {
							window.location.href = '/menu/';
					}, 1500);
			} else {
					resultDiv.innerHTML = `<div class="alert alert-danger">${data}</div>`;
			}
	})
	.catch(error => {
			resultDiv.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
			console.error('Error:', error);
	});
}
