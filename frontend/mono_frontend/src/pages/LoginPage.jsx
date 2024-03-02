import React, { useState } from 'react'
import { Form, json, redirect } from 'react-router-dom'
import PopUpManager from '../components/PopUpManager'
import { BACKEND_URL } from '../config/envs'

export default function LoginPage() {
	const [loginData, setLoginData] = useState({ tg_id: '', password: '' })

	const handleChange = e => {
		setLoginData({ ...loginData, [e.target.name]: e.target.value })
	}

	return (
		<div className='login-container'>
			<Form method='post' className='login-form'>
				<label htmlFor='tg_id'>Login:</label>
				<input
					type='text'
					id='tg_id'
					name='tg_id'
					value={loginData.login}
					onChange={handleChange}
					required
				/>

				<label htmlFor='password'>Password:</label>
				<input
					type='password'
					id='password'
					name='password'
					value={loginData.password}
					onChange={handleChange}
					required
				/>

				<button type='submit'>Submit</button>
			</Form>
		</div>
	)
}

export async function action({ request }) {
	const data = await request.formData()
	const authData = {
		tg_id: data.get('tg_id'),
		password: data.get('password')
	}

	const endpoint = `${BACKEND_URL}/account/token/`
	const response = await fetch(endpoint, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(authData)
	})

	const respData = await response.json()

	if (!response.ok) {
		let message = respData.detail || 'Not valid credentials to login'
		PopUpManager.addPopUp(message)
		return json({ message: message }, { status: response.status })
	}
	const token = respData.access
	const refresh = respData.refresh
	//
	localStorage.setItem('token', token)
	localStorage.setItem('refresh', refresh)

	return redirect('/')
}
