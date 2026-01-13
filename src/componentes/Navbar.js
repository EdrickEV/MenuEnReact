import React from 'react'
import { Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <>
                <nav className="navbar navbar-expand-lg bg-primary">
                    <div className="container-fluid">
                        <Link className="navbar-brand text-light" to='/'>Bienvenida</Link>
                        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" 
                                aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                        </button>
                        <div className="collapse navbar-collapse" id="navbarNavDropdown">
                            <ul className="navbar-nav">
                                <li className="nav-item">
                                    <Link className="nav-link active text-light" aria-current="page" to='/inicio'>Inicio</Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link text-light" to='/destacados'>Destacados</Link>
                                </li>
                                <li className="nav-item dropdown">
                                <Link className="nav-link dropdown-toggle text-light" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    Contactanos
                                </Link>
                                <ul className="dropdown-menu bg-primary">
                                    <li><Link className="dropdown-item text-body" to="/contacto">Contactanos</Link></li>
                                    <li><Link className="dropdown-item text-body" to="/informaciones">Informaciones</Link></li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        </>
    )
}

export default Navbar 