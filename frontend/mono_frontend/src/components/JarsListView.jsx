import { JarsContent } from './JarsContent'

export const JarsListView = ({ jarsData }) => {
	let totalSum = null

	if (jarsData) {
		totalSum = jarsData.reduce((sum, jar) => sum + jar.balance / 100, 0)
		totalSum = Number(totalSum).toFixed(2)
	}

	return (
		<div className='jars'>
			<div className='jars__box'>
				<h1 className='jars__title'>Jars</h1>
				<p className='jars__textMoney'>
					Total balance in all your JARS: {totalSum} ₴
				</p>
				<ul className='jars__list'>
					{jarsData.map((jar, index) => (
						<li key={index} className='jars__item'>
							<JarsContent jar={jar} />
						</li>
					))}
				</ul>
			</div>
		</div>
	)
}
