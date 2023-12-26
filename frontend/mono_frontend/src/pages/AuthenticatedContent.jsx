import {Outlet} from 'react-router-dom';

export default function AuthenticatedContent() {

    return (
        <>
            <header>
                <nav>
                    <ul>
                        <li><a href="#main" className="nav-link">Main</a></li>
                        <li><a href="#info" className="nav-link">Info</a></li>
                        <li><a href="#logout" className="nav-link">Logout</a></li>
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
