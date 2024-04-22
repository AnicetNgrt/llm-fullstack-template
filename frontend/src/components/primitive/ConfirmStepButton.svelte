<script>
    import { Button } from 'flowbite-svelte';
    import { ArrowRightOutline } from 'flowbite-svelte-icons';

    export let onClick = () => {};
</script>

<Button on:click={onClick} class="w-full1 bg-gradient-to-tr from-primary-400 to-primary-500 hover:bg-gradient-to-bl">
    <slot/> <ArrowRightOutline class="w-3.5 h-3.5 ms-2" />
</Button>