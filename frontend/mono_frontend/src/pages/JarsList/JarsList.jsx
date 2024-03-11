import { useRouteLoaderData } from 'react-router-dom'
import './JarsList.css'
import { useEffect, useState } from 'react'
import { BACKEND_URL } from '../../config/envs'
import { JarsListView } from '../../components/JarsListView'
import PopUpManager from '../../components/PopUpManager'

export const getJars = async function (token) {
	const endpoint = `${BACKEND_URL}/monobank/monojars`

	const response = await fetch(endpoint, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
	const data = await response.json()

	if (!response.ok) {
		return null
	}
	return data
}

export const JarsList = () => {
	const token = useRouteLoaderData('token')
	const [jarsData, setJarsData] = useState(null)

	useEffect(() => {
		let ignoreErrors = false
		const fetchData = async function () {
			try {
				const jarsResult = await getJars(token)
				setJarsData(jarsResult)
			} catch (error) {
				if (!ignoreErrors) {
					ignoreErrors = true
					PopUpManager.addPopUp(
						`Error fetching jars data: ${error.message}`,
						'error'
					)
				}
			}
		}

		const ignore = fetchData()
		return () => {
			ignoreErrors = true
		}
	}, [token])

	return <>{jarsData && <JarsListView jarsData={jarsData} />}</>
}
