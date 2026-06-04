export default function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-gray-400 dark:text-gray-600">
        &copy; {new Date().getFullYear()} — Google Cloud Rapid Agent Hackathon (MongoDB Track)
      </div>
    </footer>
  )
}
