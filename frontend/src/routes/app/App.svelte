<script>
	import useUserInfos from '$lib/userInfos';
	import { usePayloads } from '$lib/session';
	import { writable } from 'svelte/store';
	import { onDestroy } from 'svelte';

	export let sessionName;
	export let createdSessionId;
	export let sessions;
	export let selectedSessionId;
	export let onSessionCreated;
	export let onPayloadReceived;
	export let handleChangeSession;
	export let handleNewSession;

	let _ = useUserInfos();
	let payloads = writable([]);
	let message = '';

	function handlePayloadReceived(payload) {
		onPayloadReceived(payload);

		payloads.update((inner) => {
			inner.push(payload);
			return inner;
		});
	}

	let { state, sendPayload, disconnect } = usePayloads(
		selectedSessionId,
		onSessionCreated,
		handlePayloadReceived
	);

	function handleSendMessage() {
		$sendPayload({ type: 'message', message: message });
		message = '';
		state.set('closed');
	}

	onDestroy(() => {
		disconnect();
	});
</script>

<svelte:head>
	<title>{sessionName}</title>
</svelte:head>

{#if $state == 'opened'}
	<div class="flex w-fit flex-col gap-1">
		<textarea class=" w-[30ch]" bind:value={message} />
		<button class="bg-primary-200 hover:bg-primary-100" on:click={handleSendMessage}> send </button>
	</div>
{/if}
<div class="flex gap-4">
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div class="flex flex-col gap-2">
		<div class="text-xs">SESSIONS</div>
		{#each sessions as session}
			{#if session.id == selectedSessionId || session.id == createdSessionId}
				<div>
					{session.title}
				</div>
			{:else}
				<!-- svelte-ignore a11y-click-events-have-key-events -->
				<!-- svelte-ignore a11y-no-static-element-interactions -->
				<div
					class="cursor-pointer text-blue-400 hover:underline"
					on:click={() => handleChangeSession(session)}
				>
					{session.title}
				</div>
			{/if}
		{/each}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div class="cursor-pointer text-green-500 hover:underline" on:click={handleNewSession}>
			new session
		</div>
	</div>

	<div class="flex flex-col gap-2 max-w-[55ch] break-all">
		<div class="text-xs">PAYLOADS</div>
		{#each $payloads as payload}
			<div>
				{@html JSON.stringify(payload).replaceAll('\n', '<br/>').replaceAll(' ', '&nbsp;')}
			</div>
		{/each}
	</div>
</div>
