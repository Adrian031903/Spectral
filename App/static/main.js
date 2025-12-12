
async function getUserData(){
    const response = await fetch('/api/users');
    return response.json();
}

function loadTable(users){
    const table = document.querySelector('#result');
    for(let user of users){
        const username = user.username || "";
        const parts = username.trim().split(/\s+/).filter(Boolean);
        const firstName = parts[0] || username;
        const lastName = parts.length > 1 ? parts.slice(1).join(' ') : "";
        table.innerHTML += `<tr>
            <td>${user.id}</td>
            <td>${firstName}</td>
            <td>${lastName}</td>
        </tr>`;
    }
}

async function main(){
    const users = await getUserData();
    loadTable(users);
}

main();