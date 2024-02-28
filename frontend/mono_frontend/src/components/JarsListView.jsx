import { Link } from 'react-router-dom'
import { JarIcon } from './JarIcon'
import { ProgressBar } from './ProgressBar'

export const JarsListView = ({ jarsData }) => {
	let totalSum = null

	if (jarsData) {
		totalSum = jarsData.reduce((sum, jar) => sum + jar.balance / 100, 0)
		totalSum = Number(totalSum).toFixed(2)
	}

	const calcTotalProc = function (balance, goal) {
		return String(Math.round((balance / goal) * 100) + '%')
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
							<Link className='jars__link' to='#'>
								<div className='jars__iconBox'>
									<JarIcon />
								</div>

								<h3 className={jar?.goal ? 'marginGoal' : 'marginWithoutGoal'}>
									{jar.title}
								</h3>
								{jar?.goal && (
									<ProgressBar
										calcFunc={() => calcTotalProc(jar.balance, jar.goal)}
									/>
								)}
								<p className='jars__text'>
									Accumulated {(jar.balance / 100).toFixed(2)}{' '}
									{jar.currency.symbol}
								</p>
							</Link>
						</li>
					))}
				</ul>
			</div>
		</div>
	)
}
