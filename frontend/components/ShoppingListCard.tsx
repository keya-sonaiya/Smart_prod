import { ShoppingListItem } from "@/lib/api";

interface ShoppingListCardProps {
  items: ShoppingListItem[];
}

export default function ShoppingListCard({ items }: ShoppingListCardProps) {
  return (
    <div className="border rounded-lg p-4 mt-4 bg-gray-50">
      <h3 className="font-semibold mb-2">Your Shopping List</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left border-b">
            <th className="py-1">Item</th>
            <th>Qty</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={`${item.name}-${i}`} className="border-b last:border-0">
              <td className="py-1">{item.name}</td>
              <td>
                {item.quantity} {item.unit}
              </td>
              <td>{item.relation_type === "REQUIRES" ? "Required" : "Optional"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
