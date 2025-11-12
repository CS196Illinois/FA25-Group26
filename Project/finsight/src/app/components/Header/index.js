import styles from './Header.module.css';
import Link from 'next/link';

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
                    Logo
                </div>
            </div>
        </header>
    );
}