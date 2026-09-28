import { useParams } from "react-router-dom";
import { useLive } from "../ui";
import { BoardBody } from "./Board";

export default function AdminBoard() {
  const { code = "TALLER" } = useParams();
  const { live, error } = useLive(code);
  return <BoardBody code={code} live={live} error={error} />;
}
