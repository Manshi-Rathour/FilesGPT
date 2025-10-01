export default function ChatHistory({ history, onSelect }) {
  return (
    <div className="w-1/4 bg-white rounded-2xl shadow p-4 flex flex-col gap-4">
      <div>
        <h2 className="text-lg font-bold mb-2">Chat History</h2>
        {history.length === 0 ? (
          <p className="text-sm text-gray-600">No previous chats</p>
        ) : (
          history.map((item, idx) => (
            <button
              key={idx}
              onClick={() => onSelect(item)}
              className="w-full text-left px-3 py-2 border rounded-lg mb-1 hover:bg-gray-100"
            >
              {item}
            </button>
          ))
        )}
      </div>
    </div>
  );
}
