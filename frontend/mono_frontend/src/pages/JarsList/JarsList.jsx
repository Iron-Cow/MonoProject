import { Link, useRouteLoaderData } from 'react-router-dom'
import './JarsList.css'
import { useEffect, useState } from 'react'
import { BACKEND_URL } from '../../config/envs'
import { JarIcon } from '../../components/JarIcon'
import { ProgressBar } from '../../components/ProgressBar'
import { JarsListView } from '../../components/JarsListView'

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
		const fetchData = async function () {
			try {
				const access = await getJars(token)
				setJarsData(access)
			} catch (error) {
				console.error('Error fetching card data:', error)
			}
		}

		let ignore = fetchData()
	}, [token])

	return <>{jarsData && <JarsListView jarsData={jarsData} />}</>
}
