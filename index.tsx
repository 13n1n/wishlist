import "react";
import { Elysia } from "elysia";
import { html } from "@elysiajs/html";
import * as elements from "typed-html";


require('console-stamp')(console, '[HH:MM:ss.l]');

const app = new Elysia()
    .use(html())
    .get("/", ({ html }) =>
        html(
            <BaseHTML>
                <div
                    class="flex w-full h-screen justify-center items-center"
                    hx-get="/todos"
                    hx-trigger="load"
                    hx-swap="innerHTML"
                >
                    Loading...
                </div>
            </BaseHTML>
        )
    )
    .get("/todos", () => <TodoList todos={db} />)
    .post("/clicked", () => <div>Serverside</div>)
    .post("/todos/toggle/:id", ({ params }) => {
        const todo = db.find((todo) => todo.id.toString() === params.id);
        if (todo) {
            todo.completed = !todo.completed;
            return <TodoItem {... todo} />;
        }
    })
    .post("/todos/:id", ({params, body}) => {
        const todo = db.find((todo) => todo.id.toString() === params.id);
        console.log(body);
        if (todo) {
            todo.title = body.title;
            todo.content = body.content;
            return <TodoItem {... todo} />;
        }
    })
    .delete("/todos/:id", ({ params }) => {
        const todo = db.find((todo) => todo.id.toString() === params.id);
        if (todo) {
            db.splice(db.indexOf(todo), 1);
        }
    })
    .listen(3000);

console.log(`🦊 Elysia started! 🦊`)

const BaseHTML = ({ children }: elements.Children) => `
<!DOCTYPE html>
<html lang=ru>

<head>
    <title>Wishlist</title>
    <script src="https://unpkg.com/htmx.org@1.9.3"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body>
    ${children}
</body>
`

type Todo = {
    id: number;
    title: string;
    content: string;
    completed: boolean;
}

const db: Todo[] = [
    { id: 1, title: "new house", content: "big big house", completed: false },
    { id: 2, title: "new car", content: "very fast car", completed: true },
]

function TodoItem({ title, content, completed, id}: Todo) {
    return (
        <form
            id={`${id}`}
            hx-post={`/todos/${id}`}
            hx-trigger="changed"
            hx-swap="innerHTML">
                <div class="flex flex-row space-x-3">
                    <input
                        name="title"
                        type="text"
                        value={`${title}`} />
                    <input
                        name="completed"
                        type="checkbox"
                        checked={completed} />
                    <button
                        hx-delete={`/todos/${id}`}
                        hx-target="closest form"
                        hx-swap="outerHTML"
                        class="text-red-500"
                    >X</button>
                </div>
                <textarea
                    name="content"
                    style="display: none">
                        {content}
                </textarea>
        </form>
    )
}

function TodoList({ todos } : { todos: Todo[] }) {
    return (
        <div>
            { todos.map((todo) => {
                return <TodoItem {... todo} />
            })}
        </div>
    )
}