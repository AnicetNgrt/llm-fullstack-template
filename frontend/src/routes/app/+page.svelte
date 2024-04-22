<script>
	import { page } from '$app/stores';
	import useUserInfos from '$lib/userInfos';
	import { useSessions } from '$lib/session';
	import { writable } from 'svelte/store';
	import App from './App.svelte';

	let selectedSessionId = writable($page.url.searchParams.get('id') ?? 'new' + Math.random());
	let createdSessionId = -1;
	let sessionName = 'new session';
	let { sessions, refreshSessions } = useSessions();
	let _ = useUserInfos();

	async function onSessionCreated(newSessionId) {
		console.log('new session created', newSessionId);
		window.history.replaceState({}, '', `/app?id=${newSessionId}`);
		await refreshSessions();
		sessionName =
			$sessions.find((session) => session.id === newSessionId)?.title ?? 'unknown session';
		createdSessionId = newSessionId;
	}

	function onPayloadReceived(payload) {
		sessions.update((inner) => {
			const session = inner.find(
				(session) => session.id === createdSessionId || session.id === $selectedSessionId
			);

			if (session) {
				session.last_activity_at = new Date(new Date().toISOString());
			}

			return inner;
		});
	}

	function handleChangeSession(session) {
		selectedSessionId.set(session.id);
		window.history.replaceState({}, '', `/app?id=${session.id}`);
		sessionName = session.title;
		createdSessionId = -1;
	}

	function handleNewSession() {
		const newSessionId = 'new' + Math.random();
		selectedSessionId.set(newSessionId);
		window.history.replaceState({}, '', `/app?id=${newSessionId}`);
		sessionName = 'new session';
		createdSessionId = -1;
	}
</script>

<svelte:head>
	<title>{sessionName}</title>
</svelte:head>

<main class=" flex h-screen max-w-full flex-col gap-3 font-mono">
	{#key $selectedSessionId}
		<App
			{sessionName}
			{createdSessionId}
			sessions={$sessions}
			selectedSessionId={$selectedSessionId}
			{onSessionCreated}
			{onPayloadReceived}
			{handleChangeSession}
			{handleNewSession}
		/>
	{/key}
</main>
