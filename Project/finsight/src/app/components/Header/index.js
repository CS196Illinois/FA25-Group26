import Image from 'next/image'; 
import styles from './Header.module.css';
import Link from 'next/link';
import logoImageSource from './finFinal.png';

export default function Header() {
    return (
        <header className={styles.header}>
            <div className={styles.container}>
                <div className={styles.website}>
                    <Link href="/">
                        <h1>FinSight</h1>
                    </Link>
                </div>

                <nav className={styles.nav}>
                    <Link href="/about">About</Link>
                    <Link href="/portfolio-tracker">Portfolio Tracker</Link>
                    <Link href="/model-insights">Model Insights</Link>
                </nav>

                <div className={styles.searchBar}>
                    <input type="text" placeholder="Search" />
                </div>

                <div className={styles.logo}>
                    <Image 
                        src={logoImageSource}   
                        alt="FinSight Logo"
                        width={45}                // You can adjust this size
                        height={45}               // You can adjust this size
                    />
                </div>
            </div>
        </header>
    );
}