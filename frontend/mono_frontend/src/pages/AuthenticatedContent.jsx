import {Link, Outlet, useLoaderData} from 'react-router-dom';

export default function AuthenticatedContent() {
    const token = useLoaderData()
    console.log("AuthenticatedContent ->", token)
    return (
        <>
            <header>
                <nav>
                    <ul>
                        <li>
                            <Link to="/logout" role="button" className="nav-link">Logout</Link>
                        </li>
                    </ul>
                </nav>
            </header>
            <main>
                {/* {navigation.state === 'loading' && <p>Loading...</p>} */}
                <Outlet/>
            </main>
        </>
    );
}
