import { Link, Outlet, useLoaderData } from 'react-router-dom'
import '../AuthenticatedContent/AuthenticatedContent.css'

export default function AuthenticatedContent() {
	return (
		<>
			<header className='header'>
				<div className='header__box'>
					<nav className='header__nav'>
						<ul className='header__list'>
							<li className='header__item'>
								<Link className='header__link' to='/cards'>
									Cards
								</Link>
							</li>
							<li className='header__item'>
								<Link className='header__link' to='jars'>
									Jars
								</Link>
							</li>
							<li className='header__item'>
								<Link className='header__link' to='#'>
									Transactions
								</Link>
							</li>
						</ul>
						<div className='header__logout'>
							<Link to='/logout' role='button' className='header__link'>
								Logout
							</Link>
						</div>
					</nav>
				</div>
			</header>
			<main>
				{/* {navigation.state === 'loading' && <p>Loading...</p>} */}
				<Outlet />
			</main>
		</>
	)
}
