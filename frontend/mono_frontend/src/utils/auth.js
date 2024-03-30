import { BACKEND_URL } from '../config/envs'
import { action as logoutAction } from '../pages/Logout'

export async function getAuthToken() {
	const refresh = localStorage.getItem('refresh')
	let token
	try {
		token = await refreshAuthToken(refresh)
	} catch {
		return null
	}
	if (!token) {
		return null
	}
	return token
}

async function refreshAuthToken(refresh) {
	const endpoint = `${BACKEND_URL}/account/token-refresh/`
	const response = await fetch(endpoint, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ refresh: refresh })
	})
	const data = await response.json()

	if (!response.ok) {
		return null
	}

	return data.access
}

export async function checkAuthLoader() {
	const token = await getAuthToken()

	if (!token) {
		return logoutAction()
	}
	return token
}
