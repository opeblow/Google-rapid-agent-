import { Link, useLocation } from 'react-router-dom'
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'

export default function Navbar({ dark, toggleDark }) {
  const location = useLocation()

  const links = [
    { to: '/plans', label: 'My Plans' },
  ]

  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <nav className="sticky top-0 z-50 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-7 h-7 rounded-lg bg-gray-950 dark:bg-white flex items-center justify-center text-[10px] font-bold text-white dark:text-gray-950">FF</div>
            <span className="font-semibold text-sm text-gray-900 dark:text-white group-hover:text-gray-500 dark:group-hover:text-gray-400 transition-colors">
              Fanfare
            </span>
          </Link>

          <div className="flex items-center gap-5">
            {links.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-sm transition-colors ${
                  isActive(link.to)
                    ? 'text-gray-900 dark:text-white font-medium'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={toggleDark}
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400"
              aria-label="Toggle theme"
            >
              {dark ? <SunIcon className="w-4 h-4" /> : <MoonIcon className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
